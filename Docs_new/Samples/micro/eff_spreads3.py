# measurse to alculate average
measures = ['DollarEffectiveSpread', 'PercentEffectiveSpread']

# getting averages of Dollar Realized Spreads and Percent Realized Spreads
eff_spreads_ave = taq.taq.compute_averages_ave_sw_dw(eff_spreads_df, measures)
eff_spreads_ave