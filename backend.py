# backend.py
import numpy as np
import yfinance as yf
from scipy import stats

class PortfolioOptimizer:
    def __init__(self, assets, phi=250, allow_shorts=False, sampling_rate="1d", total=10000):
        self.assets = assets
        self.N = len(assets)
        self.phi = phi
        self.allow_shorts = allow_shorts
        self.sampling_rate = sampling_rate
        self.total = total

        self.prices = None

        self.cov_matrix = None
        self.corr_matrix = None

        self.x = (np.ones(self.N)/ self.N) * total 
        self.x = self.x.reshape(-1,1)

        self.mean_returns = None
        self.returns = None
        self.std = None
        self.expected_returns = None
        self.risk = None

    def fetch_data(self):
        """Download price data using yfinance based on sampling_rate."""
        self.prices = yf.download(
            tickers=self.assets,
            period="1y",
            interval=self.sampling_rate
        )["Close"].dropna()
        self.returns = self.prices.pct_change().dropna()
        self.mean_returns = self.returns.mean()
        self.mean_returns = self.mean_returns.values.reshape(-1,1)

        

    def compute_cov_corr(self):
        """Compute covariance and correlation matrices."""
        self.cov_matrix = self.returns.cov()
        self.corr_matrix = self.returns.corr()
        return self.cov_matrix, self.corr_matrix
    
    def f(self, x,sigma, mu,phi):
        return 0.5* x.T @ sigma @ x - phi * mu.T @ x

    def grad_L(self, x, sigma, mu,phi):
        return sigma @ x - phi * mu


    def project_simplex(self, y, T=1):
        # y: numpy array
        n = len(y)
        u = np.sort(y)[::-1]
        cssv = np.cumsum(u)
        rho = np.where(u + (T - cssv) / (np.arange(n) + 1) > 0)[0][-1]
        theta = (T - np.sum(u[:rho+1])) / (rho+1)
        return np.maximum(y + theta, 0)

    def pgd(self,x0, sigma, mu, phi, T, lr = 0.01, steps = 1000, tol = 1e-8):
        x= self.project_simplex(x0, T)
        history = [self.f(x,sigma,mu,phi).item()]
        for k in range(steps):
            g = self.grad_L(x, sigma, mu, phi)
            y = x - lr* g
            x_next = self.project_simplex(y,T)
            if np.linalg.norm(x_next-x)<tol:
                break
            x = x_next
            history.append(self.f(x,sigma,mu,phi).item())
        return x, history

    def run_optimization(self):
        """Run the portfolio optimization and return all results."""
        # Placeholder for your PGD or Lagrange backend
        if self.allow_shorts:
            method = "Lagrange"
            sigma = self.cov_matrix.values
            ones = np.ones((self.cov_matrix.shape[0],1))
            cov_inv = np.linalg.inv(self.cov_matrix)

            lda = (ones.T@ cov_inv @ self.mean_returns - self.phi*self.total)/(ones.T @ cov_inv @ ones)
            x_opt = ((cov_inv @ self.mean_returns)-cov_inv @ ones * lda) / self.phi
            x_opt = x_opt.flatten()
            self.x = x_opt
            
            # call your Lagrange optimization here
        else:
            method = "PGD"
            sigma = self.cov_matrix.values
            lr = 0.1
            steps = 15000
            tol = 1e-8
            x_opt, hist = self.pgd(self.x,sigma,self.mean_returns,self.phi,self.total,lr,steps,tol)
            self.x = x_opt
            # call your PGD optimization here

        # Example dummy outputs
        self.x = self.x.reshape(-1, 1)
        n = len(self.assets)
        self.expected_returns = float(self.mean_returns.T @ self.x)
        self.risk = np.random.normal(0.05, 0.01, n)
        self.std = np.sqrt(self.x.T @ sigma @ self.x).item()
        par = stats.norm.ppf(0.99)
        self.risk = (par * self.std)/self.total * 100

        return {
            "assets": self.assets,
            "pvec": self.x.flatten(),
            "expected_returns": self.expected_returns,
            "mr": self.mean_returns.flatten(),
            "risk": self.risk,
            'std': self.std,
            "method": method
        }
