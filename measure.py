### measure libraby version 1.5.1
import numpy as np
import matplotlib.pyplot as plt

# Settings
linreg_change = 0.00001 # min relative change per step to end linear regression
minfloat = 1e-80 # replaces zeros in linreg

# Variables for export
sqrt = np.sqrt
exp = np.exp
ln = np.log
log10 = np.log10
sin = np.sin
cos = np.cos
tan = np.tan
arctan = np.arctan
pi = np.pi
euler_e = np.e
c = 2.99792458e8 # Speed of light
h = 6.626070040e-34 # Planck's constant
dh = 8.1e-42 # Uncertanty of Planck's constant
e = 1.6021766208e-19 # Elementary charge
de = 9.8e-28 # Uncertanty of the elementary charge
T0 = 273.15 # Zero Celsius in Kelvin
g = 9.80984 # Gravitantional Acceleration in Heidelberg 
dg = 2e-5 # Uncertanty of the gravitational Acceleration

def mean_value(x):
  s = 0.0
  for i in range(len(x)):
    s += x[i]
  return s / len(x)

def std_dev_e(x):
  qs = 0.0
  for i in range(len(x)):
    qs += (x[i] - mean_value(x))**2
  return np.sqrt(qs / (len(x) - 1))

def std_dev_m(x):
  return std_dev_e(x) / np.sqrt(len(x))

def signval(val, err=0.0):
  if (err == 0.0):
    return "{:g}".format(val)
  if ("{:.1e}".format(err)[0] == "9" and "{:.0e}".format(err)[0] == "1"):
    err = float("{:.0e}".format(err))
  firstdigit = int("{:.1e}".format(err)[0])
  if (firstdigit <= 2):
    round2 = 1
    errstr = "{:.1e}".format(err)
  else:
    round2 = 0
    errstr = "{:.0e}".format(err)
  expdiff = int(np.floor(np.log10(abs(val))) - np.floor(np.log10(err)))
  if (expdiff < 0):
    sdigits = 0
    if (round2 != 1 or expdiff != -1):
      val = 0.0
  else:
    sdigits = expdiff + round2
  valstr = "{:.{digits}e}".format(val, digits=sdigits)
  return valstr + " ± " + errstr

def val(name, val, err=0.0):
  return name + ": " + signval(val, err)

def lst(name, val, err=[]):
  # todo: format data to make values align nicely, needs modifying of signval
  if (err == []):
    err = [0.0 for i in range(len(val))]
  tmp = name + ":"
  for i in range(len(val)):
    tmp +=  "\n " + signval(val[i], err[i])
  return tmp

def sig(name, val1, dVal1, val2, dVal2=0.0):
  nominator = abs(val1 - val2)
  denominator = np.sqrt(dVal1**2 + dVal2**2)
  if (nominator == 0.0):
    sigstr = "0"
  elif (denominator == 0.0):
    sigstr = "∞"
  else:
    sigma = nominator / denominator
    if (sigma < 0.95):
      digits = int(abs(np.floor(np.log10(sigma))))
    elif (sigma < 3.95):
      digits = 1
    else:
      digits = 0
    sigstr = "{:.{digits}f}".format(sigma, digits = digits)
  return name + ": " + sigstr + "σ"

def chi2(yo, dyo, ye, dye=[]):
  if (dye == []):
    dye = [0.0 for i in range(len(ye))]
  chi2 = 0.0
  for i in range(len(yo)):
    chi2 += (yo[i] - ye[i])**2 / (dyo[i]**2 + dye[i]**2)
  return chi2

def chi2_red(yo, dyo, ye, dye=[], dof=0):
  if (dof == 0):
    dof = len(ye)
  return chi2(yo, dyo, ye, dye) / dof

def showfigs():
  plt.show()

class table:
  def __init__(self, data, rowLbls, colLbls, title="", fig=0):
    self.figure = plt.figure(fig)
    plt.clf()
    plt.axis("off")
    plt.table(cellText=data, rowLabels=rowLbls, colLabels=colLbls, loc="center")

class plot:
  def __init__(self, title="", xlabel="", ylabel="", fig=0, scale="linlin"):
    self.figure = plt.figure(fig)
    plt.clf()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    if (scale == "linlin"):
      plt.ticklabel_format(style="sci", axis="both", scilimits=(-2,3))
    elif (scale == "linlog"):
      plt.yscale("log")
      plt.ticklabel_format(style="sci", axis="x", scilimits=(-2,3))
    elif (scale == "loglin"):
      plt.xscale("log")
      plt.ticklabel_format(style="sci", axis="y", scilimits=(-2,3))
    elif (scale == "loglog"):
      plt.yscale("log")
      plt.xscale("log")

  plt = plt

  def plotdata(self, x, y, dy=[], dx=[], label=""):
    if (dx == []):
      dx = [0.0 for i in range(len(x))]
    if (dy == []):
      dy = [0.0 for i in range(len(y))]
    plt.errorbar(x, y, dy, dx, label=label, fmt='o', markersize=3)
    if (label != ""):
      plt.legend()
  
  def plotfunc(self, x, y, label=""):
    plt.plot(x, y, label=label)
    if (label != ""):
      plt.legend()

def linreg(x, y, dy, dx=[], lrplot=None, graphname=""):
  def linreg_iter(x, y, dy):
    [s0, s1, s2, s3, s4] = [0.0, 0.0, 0.0, 0.0, 0.0]
    for i in range(len(x)):
      if (dy[i] == 0.0):
        dy[i] = minfloat
      s0 += dy[i]**-2
      s1 += x[i] * dy[i]**-2
      s2 += y[i] * dy[i]**-2
      s3 += x[i]**2 * dy[i]**-2
      s4 += x[i] * y[i] * dy[i]**-2
    eta = s0 * s3 - s1**2
    g = (s0 * s4 - s1 * s2) / eta
    dg = np.sqrt(s0 / eta)
    b = (s3 * s2 - s1 * s4) / eta
    db = np.sqrt(s3 / eta)
    return [g, dg, b, db]

  iter0 = linreg_iter(x, y, dy)
  result = []
  if (dx == []):
    dx = [0.0 for i in range(len(x))]
    result = iter0
  else:
    g = iter0[0]
    g_old = g * (1 - 2 * linreg_change)
    while (abs(1 - g_old / g) >= linreg_change):
      g_old = g
      dy = [np.sqrt((g * dx[i])**2 + dy[i]**2) for i in range(len(dy))]
      g = linreg_iter(x, y, dy)[0]
    result = linreg_iter(x, y, dy)
  if (lrplot != None):
    [g, dg, b, db] = result
    min_x = np.argmin(x)
    max_x = np.argmax(x)
    xint = [x[min_x] - dx[min_x], x[max_x] + dx[max_x]]
    yfit = [g * xint[i] + b for i in range(2)]
    yerr = [(g + dg) * xint[i] + (b - db) for i in range(2)]
    datalabel = prefix = ""
    if (graphname != ""):
      prefix = graphname + ": "
      datalabel = prefix + "data points"
    lrplot.plotdata(x, y, dy, dx, label=datalabel)
    lrplot.plotfunc(xint, yfit, label=prefix+"line of best fit")
    lrplot.plotfunc(xint, yerr, label=prefix+"line of uncertainty")
  return result

def lin_yerr(x, dx, y, dy):
  g = linreg(x, y, dx, dy)
  new_dy = [np.sqrt(dy[i]**2 + (g * dx[i])**2) for i in range(len(dy))]
  return new_dy
