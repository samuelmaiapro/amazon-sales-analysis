# src/growth_metrics.py

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


class GrowthAnalytics:
    """
    Classe para análises avançadas de crescimento e tendências.
    """

    def __init__(self, df):
        self.df = df.copy()
        self._prepare_data()

    def _prepare_data(self):
        """Prepara dados com múltiplas granularidades temporais."""
        self.df['date'] = pd.to_datetime(self.df['order_date'])
        self.df['year'] = self.df['date'].dt.year
        self.df['month'] = self.df['date'].dt.month
        self.df['year_month'] = self.df['date'].dt.to_period('M')

    def calculate_growth_metrics(self, period='month', metric='total_revenue'):
        """Calcula métricas de crescimento."""
        if period == 'month':
            grouped = self.df.groupby('year_month')[metric].sum().reset_index()
            grouped['period_label'] = grouped['year_month'].astype(str)
        else:
            grouped = self.df.groupby('date')[metric].sum().reset_index()
            grouped['period_label'] = grouped['date'].dt.strftime('%Y-%m-%d')

        grouped['previous_period'] = grouped[metric].shift(1)
        grouped['growth_abs'] = grouped[metric] - grouped['previous_period']
        grouped['growth_pct'] = (grouped['growth_abs'] / grouped['previous_period'] * 100).round(2)
        grouped['growth_pct'] = grouped['growth_pct'].fillna(0)

        return grouped

    def momentum_score(self):
        """Calcula score de momentum (0-100)."""
        monthly = self.calculate_growth_metrics(period='month')

        if len(monthly) < 3:
            return {
                'score': 50,
                'components': {'growth': 0, 'consistency': 50, 'trend': 50},
                'interpretation': "📊 **Dados insuficientes** - Necessário mais histórico"
            }

        recent = monthly.tail(3)
        growth_component = recent['growth_pct'].mean()
        consistency_component = 100 - min(100, abs(recent['growth_pct'].std()))
        trend = recent['growth_pct'].iloc[-1] - recent['growth_pct'].iloc[:-1].mean()
        trend_component = 50 + min(50, max(-50, trend))

        score = (max(0, growth_component) * 0.4 + consistency_component * 0.3 + trend_component * 0.3)
        score = max(0, min(100, score))

        return {
            'score': round(score, 1),
            'components': {
                'growth': round(max(0, growth_component), 1),
                'consistency': round(consistency_component, 1),
                'trend': round(trend_component, 1)
            },
            'interpretation': self._interpret_score(score)
        }

    def _interpret_score(self, score):
        """Interpretação do score."""
        if score >= 80:
            return "🚀 **Crescimento Acelerado**"
        elif score >= 60:
            return "📈 **Crescimento Sustentável**"
        elif score >= 40:
            return "⚖️ **Estabilidade**"
        elif score >= 20:
            return "📉 **Desaceleração**"
        else:
            return "⚠️ **Declínio**"

    def identify_growth_drivers(self, top_n=5):
        """Identifica drivers de crescimento."""
        dates = sorted(self.df['date'].unique())
        if len(dates) < 2:
            return {'top_growth_drivers': [], 'top_decliners': [], 'overall_growth': 0}

        mid_point = dates[len(dates) // 2]
        period1 = self.df[self.df['date'] < mid_point]
        period2 = self.df[self.df['date'] >= mid_point]

        cat_growth = []
        for category in self.df['product_category'].unique():
            rev1 = period1[period1['product_category'] == category]['total_revenue'].sum()
            rev2 = period2[period2['product_category'] == category]['total_revenue'].sum()

            total_growth = period2['total_revenue'].sum() - period1['total_revenue'].sum()

            if rev1 > 0:
                growth_pct = ((rev2 - rev1) / rev1) * 100 if rev1 > 0 else 0
                contribution = ((rev2 - rev1) / total_growth * 100) if total_growth != 0 else 0

                cat_growth.append({
                    'category': category,
                    'growth_pct': round(growth_pct, 1),
                    'contribution_pct': round(contribution, 1)
                })

        if not cat_growth:
            return {'top_growth_drivers': [], 'top_decliners': [], 'overall_growth': 0}

        growth_df = pd.DataFrame(cat_growth).sort_values('contribution_pct', ascending=False)
        overall_growth = ((period2['total_revenue'].sum() - period1['total_revenue'].sum()) /
                          period1['total_revenue'].sum() * 100) if period1['total_revenue'].sum() > 0 else 0

        return {
            'top_growth_drivers': growth_df.head(top_n).to_dict('records'),
            'top_decliners': growth_df.tail(top_n).to_dict('records'),
            'overall_growth': round(overall_growth, 1)
        }

    def forecast_growth(self, periods=3):
        """Previsão simples de crescimento."""
        monthly = self.calculate_growth_metrics(period='month')

        if len(monthly) < 3:
            return {
                'forecast_values': [],
                'forecast_growth_pct': 0,
                'confidence': 'Baixa',
                'trend_direction': 'indefinida'
            }

        x = np.arange(len(monthly))
        y = monthly['total_revenue'].values
        z = np.polyfit(x, y, 1)
        trend = np.poly1d(z)

        future_x = np.arange(len(monthly), len(monthly) + periods)
        forecast = [max(0, f) for f in trend(future_x)]

        current = y[-1]
        forecast_growth = ((forecast[-1] - current) / current) * 100 if current > 0 else 0

        return {
            'forecast_values': forecast,
            'forecast_growth_pct': round(forecast_growth, 1),
            'confidence': 'Média' if len(monthly) < 12 else 'Alta',
            'trend_direction': 'positiva' if z[0] > 0 else 'negativa'
        }

    def bcg_matrix(self):
        """Cria matriz BCG."""
        category_perf = self.df.groupby('product_category').agg({
            'total_revenue': 'sum',
            'order_id': 'nunique'
        }).reset_index()

        total_market = category_perf['total_revenue'].sum()
        category_perf['market_share'] = (category_perf['total_revenue'] / total_market * 100)

        dates = sorted(self.df['date'].unique())
        if len(dates) >= 2:
            mid_date = dates[len(dates) // 2]
            period1 = self.df[self.df['date'] < mid_date]
            period2 = self.df[self.df['date'] >= mid_date]

            growth_by_cat = []
            for cat in category_perf['product_category']:
                rev1 = period1[period1['product_category'] == cat]['total_revenue'].sum()
                rev2 = period2[period2['product_category'] == cat]['total_revenue'].sum()
                growth = ((rev2 - rev1) / rev1 * 100) if rev1 > 0 else 0
                growth_by_cat.append(growth)

            category_perf['growth'] = growth_by_cat
        else:
            category_perf['growth'] = 0

        return category_perf


def render_growth_tab(st, df_filtered):
    """Renderiza a tab de Growth Analytics."""
    st.markdown("""
    <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: white; margin: 0;'>🚀 Growth Analytics</h2>
        <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0;'>
            Análise avançada de crescimento
        </p>
    </div>
    """, unsafe_allow_html=True)

    ga = GrowthAnalytics(df_filtered)
    momentum = ga.momentum_score()

    col1, col2, col3 = st.columns(3)

    with col1:
        color = "#00C851" if momentum['score'] >= 60 else "#ffbb33" if momentum['score'] >= 40 else "#ff4444"
        emoji = "🚀" if momentum['score'] >= 60 else "⚖️" if momentum['score'] >= 40 else "⚠️"

        st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h1 style='font-size: 48px; margin: 0; color: {color};'>{emoji} {momentum["score"]}</h1>
            <p style='color: #666; margin: 0; font-size: 18px;'><b>Momentum Score</b></p>
            <p style='font-size: 14px; color: #666; margin-top: 10px;'>{momentum["interpretation"]}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        components_df = pd.DataFrame([
            {"Componente": "Crescimento", "Valor": momentum["components"]["growth"]},
            {"Componente": "Consistência", "Valor": momentum["components"]["consistency"]},
            {"Componente": "Tendência", "Valor": momentum["components"]["trend"]}
        ])
        fig = px.bar(components_df, x='Componente', y='Valor',
                     color='Componente', color_discrete_sequence=['#667eea', '#764ba2', '#FF9900'],
                     title="Componentes do Momentum")
        fig.update_layout(showlegend=False, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        forecast = ga.forecast_growth(periods=3)
        trend_color = "#00C851" if forecast['trend_direction'] == 'positiva' else "#ff4444"

        st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h4 style='margin: 0 0 15px 0;'>🔮 Projeção</h4>
            <p style='font-size: 24px; margin: 5px 0; color: {trend_color};'><b>{forecast['forecast_growth_pct']}%</b></p>
            <p style='color: #666;'>crescimento esperado</p>
            <p><b>Confiança:</b> {forecast['confidence']}</p>
            <p><b>Tendência:</b> <span style='color: {trend_color};'>{forecast['trend_direction'].upper()}</span></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    drivers = ga.identify_growth_drivers(top_n=5)

    if drivers['top_growth_drivers']:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Top Growth Drivers")
            drivers_df = pd.DataFrame(drivers['top_growth_drivers'])
            if not drivers_df.empty:
                fig = px.bar(drivers_df, x='category', y='contribution_pct', color='growth_pct',
                             color_continuous_scale='RdYlGn', title="Categorias que MAIS cresceram")
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📉 Top Decliners")
            decliners_df = pd.DataFrame(drivers['top_decliners'])
            if not decliners_df.empty:
                fig = px.bar(decliners_df, x='category', y='contribution_pct', color='growth_pct',
                             color_continuous_scale='RdYlGn_r', title="Categorias com MAIOR queda")
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"### 📊 Crescimento Geral: **{drivers['overall_growth']}%**")
        st.markdown("---")