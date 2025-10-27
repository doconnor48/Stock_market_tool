How it works?
A user selects stocks from a list + data sampling rate (15min, 30min, 1hr, 1d, 1wk, 1month)
Max number of stocks is 10 for one portfolio (so everything can be seen)
Display covariance and correlation matrices of stocks based on data scraped from yfinance
a button for (high risk(1250), low risk(50), a good medium (250)) + bar for phi (0.1 -> 10000)
A button for allowing shorts (Lagrange) vs. not allowing shorts (PGD)
An input for portfolio total (if not specified use pf_total = $10000)
Run PGD or Lagrange and output values + percentages on a column grid structure next to the covar, corr matrices
Have expected returns and 99% downside risk as sampled from a normal gaussian as percentages under that