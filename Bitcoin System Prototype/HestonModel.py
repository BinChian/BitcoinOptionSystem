import QuantLib as ql
import numpy as np

class Calibration():
    def __init__(self):
        self.day_count = ql.Actual365Fixed()
        self.calendar  = ql.NullCalendar()

        self.calculation_date = ql.Date(22, 11, 2021)
        calDate = str(self.calculation_date.to_date())
        self.spot = 57407.27

        ql.Settings.instance().evaluationDate = self.calculation_date

        self.risk_free_rate = [0.00091249886, 0.00091249886, 0.00141713916, 0.00178991217, 0.00308713517] # 2021/11/02 0D 1D 3M 6M 12M
        risk_free_rate_date = [ql.Date(22, 11, 2021), ql.Date(23, 11, 2021), ql.Date(23, 2, 2022), ql.Date(23, 5, 2022), ql.Date(23, 11, 2022)]
        self.zero_curve_ts = ql.YieldTermStructureHandle(ql.ZeroCurve(risk_free_rate_date, self.risk_free_rate, self.day_count, self.calendar))

        self.dividend_rate = 0.0
        self.dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(self.calculation_date, self.dividend_rate, self.day_count))
        
        # Dummy parameters for construct Heston model
        v0 = 0.01; kappa = 0.20; theta = 0.02; rho = -0.75; sigma = 0.50 # cookbook
        # v0 = 0.1; kappa = 0.1; theta = 0.1; rho = -0.1; sigma = 0.1
        HestonProcess = ql.HestonProcess(self.zero_curve_ts, self.dividend_ts, ql.QuoteHandle(ql.SimpleQuote(self.spot)), v0, kappa, theta, sigma, rho)
        HestonModel = ql.HestonModel(HestonProcess)
        AHE = ql.AnalyticHestonEngine(HestonModel)
        
        # 合約到期日
        expiration_dates = [ql.Date(31, 12, 2021), ql.Date(25, 3, 2022), ql.Date(24, 6, 2022)]
        # 合約標的
        strikes = [30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 120000]
        # 合約標的的隱含波動率
        data = [[1.1340, 0.9864, 0.8955, 0.8344, 0.8328, 0.8692, 0.9165, 0.9808, 1.0735],
                [1.0149, 0.9587, 0.9241, 0.9046, 0.9000, 0.9055, 0.9177, 0.9338, 0.9684],
                [0.9697, 0.9399, 0.9193, 0.9098, 0.9073, 0.9089, 0.9128, 0.9181, 0.9497]]

        # Implied Volatility Matrix
        implied_vols = ql.Matrix(len(strikes), len(expiration_dates))
        for i in range(implied_vols.rows()):
            for j in range(implied_vols.columns()):
                implied_vols[i][j] = data[j][i]
                
        black_var_surface = ql.BlackVarianceSurface(self.calculation_date, self.calendar, expiration_dates, strikes, implied_vols, self.day_count)
        
        heston_helpers = []
        black_var_surface.setInterpolation("bicubic")
        maturity_idx = 1
        date = expiration_dates[maturity_idx]

        for j, s in enumerate(strikes):
            t = (date - self.calculation_date)
            period = ql.Period(t, ql.Days)
            vol = data[maturity_idx][j]
            helper = ql.HestonModelHelper(period, self.calendar, self.spot, s, 
                                        ql.QuoteHandle(ql.SimpleQuote(vol)),
                                        self.zero_curve_ts, 
                                        self.dividend_ts)
            helper.setPricingEngine(AHE)
            heston_helpers.append(helper)
            
        HestonModel.calibrate(heston_helpers, ql.LevenbergMarquardt(), ql.EndCriteria(500, 50, 1.0e-8, 1.0e-8, 1.0e-8))

        self.theta, self.kappa, self.sigma, self.rho, self.v0 = HestonModel.params()
        self.params = {'CalDate': calDate, 'Spot': self.spot, 'v0': self.v0, 'rho': self.rho, 'kappa': self.kappa, 'theta': self.theta, 'sigma': self.sigma}
        
class MonteCarloSimulation():
    def __init__(self):
        pass
    
    def hestonModel(self, S0, mu, v0, kappa, theta, sigma, rho, step, path):
        dt = 1/365

        MU  = np.array([0, 0])
        COV = np.matrix([[1, rho], [rho, 1]])
        W = np.zeros((step, 2, path))
        for i in range(path):
            W[:,:,i]   = np.random.multivariate_normal(MU, COV, step)
        W_S = np.transpose(W[:, 0, :])
        W_v = np.transpose(W[:, 1, :])

        vt = np.zeros((path, step))
        St = np.zeros((path, step))
        vt[:, 0] = v0
        St[:, 0] = S0

        for t in range(1, step):
            vt[:, t] = np.maximum(vt[:, t-1] + kappa*(theta - vt[:, t-1])*dt + sigma*np.sqrt(np.abs(vt[:, t-1])*dt)*W_v[:, t], 0)
            St[:, t] = St[:, t-1] + mu*St[:, t-1]*dt + np.sqrt(np.abs(vt[:, t-1])*dt)*St[:, t-1]*W_S[:, t]
        return St

class VanillaOptionSimulation(Calibration):
    def __init__(self):
        super().__init__()
        
        self.HestonProcess = ql.HestonProcess(self.zero_curve_ts, self.dividend_ts, ql.QuoteHandle(ql.SimpleQuote(self.spot)), self.v0, self.kappa, self.theta, self.sigma, self.rho)
        self.HestonModel = ql.HestonModel(self.HestonProcess)
        self.AHE = ql.AnalyticHestonEngine(self.HestonModel)
        
    def callNPV(self, maturity, strike):
        year = int(maturity[0:4])
        month = int(maturity[5:7])
        day = int(maturity[8:10])
        maturity = ql.Date(day, month, year)
        europeanExer = ql.EuropeanExercise(maturity)
        vanillaPayoff = ql.PlainVanillaPayoff(ql.Option.Call, strike)
        anEuroOption = ql.EuropeanOption(vanillaPayoff, europeanExer)
        anEuroOption.setPricingEngine(self.AHE)
        return anEuroOption.NPV()
    
    def putNPV(self, maturity, strike):
        year = int(maturity[0:4])
        month = int(maturity[5:7])
        day = int(maturity[8:10])
        maturity = ql.Date(day, month, year)
        europeanExer = ql.EuropeanExercise(maturity)
        vanillaPayoff = ql.PlainVanillaPayoff(ql.Option.Put, strike)
        anEuroOption = ql.EuropeanOption(vanillaPayoff, europeanExer)
        anEuroOption.setPricingEngine(self.AHE)
        return anEuroOption.NPV()
    
class DigitalOptionSimulation(Calibration, MonteCarloSimulation):
    def __init__(self):
        super().__init__()
    
    def callNPV(self, maturity, strike, path = 20000):
        year = int(maturity[0:4])
        month = int(maturity[5:7])
        day = int(maturity[8:10])
        maturity = ql.Date(day, month, year)
        step = maturity - self.calculation_date
        S = self.hestonModel(self.spot, self.dividend_rate, self.v0, self.kappa, self.theta, self.sigma, self.rho, step, path)
        NPV = sum(S[:, -1] > strike)/path
        return NPV
    
    def putNPV(self, maturity, strike, path = 20000):
        year = int(maturity[0:4])
        month = int(maturity[5:7])
        day = int(maturity[8:10])
        maturity = ql.Date(day, month, year)
        step = maturity - self.calculation_date
        S = self.hestonModel(self.spot, self.dividend_rate, self.v0, self.kappa, self.theta, self.sigma, self.rho, step, path)
        NPV = sum(S[:, -1] < strike)/path
        return NPV

class BarrierOptionSimulation(Calibration, MonteCarloSimulation):
    def __init__(self):
        super().__init__()

    def downoutCallNPV(self, maturity, strike, downBarrier, path = 20000):
        year = int(maturity[0:4])
        month = int(maturity[5:7])
        day = int(maturity[8:10])
        maturity = ql.Date(day, month, year)
        step = maturity - self.calculation_date
        T = step/365
        r = self.zero_curve_ts.zeroRate(maturity, self.day_count, ql.Continuous).rate()
        discount_rate = np.exp(-r*T)

        S = self.hestonModel(self.spot, self.dividend_rate, self.v0, self.kappa, self.theta, self.sigma, self.rho, step, path)
        
        bool = np.sum(S > downBarrier, axis = 1)
        S = S[np.where(bool == step)]
        bool = S[:, -1] > strike
        NPV = sum((S[np.where(bool == True)][:, -1] - strike)*discount_rate)/path
        return NPV
    
    def downoutPutNPV(self, maturity, strike, downBarrier, path = 20000):
        year = int(maturity[0:4])
        month = int(maturity[5:7])
        day = int(maturity[8:10])
        maturity = ql.Date(day, month, year)
        step = maturity - self.calculation_date
        T = step/365
        r = self.zero_curve_ts.zeroRate(maturity, self.day_count, ql.Continuous).rate()
        discount_rate = np.exp(-r*T)

        S = self.hestonModel(self.spot, self.dividend_rate, self.v0, self.kappa, self.theta, self.sigma, self.rho, step, path)
        
        bool = np.sum(S > downBarrier, axis = 1)
        S = S[np.where(bool == step)]
        bool = S[:, -1] < strike
        NPV = sum(np.abs(strike - S[np.where(bool == True)][:, -1])*discount_rate)/path
        return NPV

class RateData():
    def __init__(self):
        day_count = ql.Actual365Fixed()
        calendar  = ql.NullCalendar()

        calculation_date = ql.Date(22, 11, 2021)
        spot = 57407.27

        ql.Settings.instance().evaluationDate = calculation_date

        risk_free_rate = [0.00091249886, 0.00091249886, 0.00141713916, 0.00178991217, 0.00308713517] # 2021/11/02 0D 1D 3M 6M 12M
        risk_free_rate_date = [ql.Date(22, 11, 2021), ql.Date(23, 11, 2021), ql.Date(23, 2, 2022), ql.Date(23, 5, 2022), ql.Date(23, 11, 2022)]
        self.zero_curve_ts = ql.YieldTermStructureHandle(ql.ZeroCurve(risk_free_rate_date, risk_free_rate, day_count, calendar))
    
    def getZeroCurve(self, time = 1):
        zeroCurve = []
        for i in range(time*12 + 1):
            zeroCurve.append(self.zero_curve_ts.zeroRate(i/12, ql.Compounded, ql.Annual).rate())
        return zeroCurve
        
    def getDiscountCurve(self, time = 1):
        discountCurve = []
        for i in range(time*12 + 1):
            discountCurve.append(self.zero_curve_ts.discount(i/12))
        return discountCurve