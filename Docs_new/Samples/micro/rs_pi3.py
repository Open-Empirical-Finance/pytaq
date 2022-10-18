# measurse to alculate average
measures = ['DollarRealizedSpread_LR5min', 'PercentRealizedSpread_LR5min',
            'DollarPriceImpact_LR5min', 'PercentPriceImpact_LR5min',
            'DollarRealizedSpread_EMO5min', 'PercentRealizedSpread_EMO5min',
            'DollarPriceImpact_EMO5min', 'PercentPriceImpact_EMO5min',
            'DollarRealizedSpread_CLNV5min', 'PercentRealizedSpread_CLNV5min',
            'DollarPriceImpact_CLNV5min', 'PercentPriceImpact_CLNV5min']

# getting averages of Realized Spreads and Price Impacts based on LR, EMO, CLNV
rs_pi_ave = taq.taq.compute_averages_ave_sw_dw(rs_pi_df, measures)
rs_pi_ave