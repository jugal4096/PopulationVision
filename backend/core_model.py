from sklearn.linear_model import Ridge
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

class HybridPopulationForecaster:
    def __init__(self):
        self.trend_model = Ridge()
        self.residual_model = GradientBoostingRegressor(n_estimators=200, max_depth=4, random_state=42)
        self.scaler = StandardScaler()
        self.feature_cols = []

    def predict_target_year(self, target_year, historical_df):
        trend_val = self.trend_model.predict([[target_year]])[0]
        latest_year = historical_df["Year"].max()
        latest_features = historical_df[historical_df["Year"] == latest_year][self.feature_cols]
        
        scaled_features = self.scaler.transform(latest_features)
        residual_val = self.residual_model.predict(scaled_features)[0]
        
        if target_year > latest_year:
            distance = target_year - latest_year
            decay_factor = 1 / (1 + (0.05 * distance))
            residual_val *= decay_factor
            
        return round(trend_val + residual_val)