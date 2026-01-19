# *** Set you local path ****
setwd("/home/daniel/Projects/daycent/sample/")

#get the relative executable path.

exe_path = "/home/daniel/Projects/daycent/"

list_exe = list.files(exe_path, full.names = T)
file.copy(from = list_exe, to = getwd(), overwrite = T)

# set DayCent executable 

dc_exe = "./DDcentEVI_rev491"
dc_L100 = "./DDlist100_rev491"

# print DayCent help menu
system2(command = dc_exe) 
              
#====================== equilibrium run =================================
# setup to produce no outfiles during equilibrium and base period
file.copy(from = "no_outfiles.in", to = "outfiles.in", overwrite = T)

eq_args <- "-s wooster_eq -N eq"

eq_log <- system2(command = dc_exe, 
                  args = eq_args,
                  wait = T,
                  stdout = T,
                  stderr = T) 

# base history run
bh_args <- "-s wooster_base -e eq -N base"
bh_log  <- system2(command = dc_exe,
                   args = bh_args,
                   wait = T,
                   stdout = T,
                   stderr = T) 

#====================== equilibrium run =================================
# setup to produce some outfiles during Experimental peirods 
file.copy(from = "few_outfiles.in", to = "outfiles.in", overwrite = T)

trt_args <- "-s wooster_cb_nt_blk1 -e base -N cb_nt"
trt_log <- system2(command = dc_exe,
                   args = trt_args,
                   wait = T,
                   stdout = T,
                   stderr = T) 

# extract and read equilibrium output from .bin file
lis_args <- paste("cb_nt wooster few_outvars.txt")
lis_log <- system2(command = dc_L100, 
                   args = lis_args,
                   wait = T,
                   stdout = T,
                   stderr = T)

wooster_lis <- read.table(file = "wooster.lis", skip = 3)
names(wooster_lis) <-  c("time", "crpval", "cgrain", "accrst", "agcprd", "bgcjprd", "bgcmprd",
					"cinput", "somsc", "fertot11", "omadtot", "omaetot1", "strmac2", "volpac")
wooster_lis$id <- 1:nrow(wooster_lis)

# wooster measured soc 
# To make sure the time and year are lined up properly,
# uncomment and run the code and enter the row-id in column id of wooster_soc data frame below.

# wooster_lis[which(wooster_lis$time %in% c(1962, 1971, 1980, 1992)), ]
#     time  crpval  cgrain  accrst  agcprd bgcjprd bgcmprd  cinput    somsc fertot11 omadtot omaetot1 strmac2 volpac  id
# 133 1962  GCP158   0.000 623.228   0.000     0.0   0.000 775.273 4748.845      0.0       0        0   1.410  0.142 133
# 134 1962    G321   0.000   0.000   0.000     0.0   0.000   0.000 4748.845      0.0       0        0   0.000  0.000 134
# 143 1971    C620 315.060   0.000 572.836   137.6   7.242 382.872 5316.113     27.7       0        0   2.467  0.491 143
# 152 1980 SYBN100 156.147   0.000   0.000     0.0   0.000 302.834 5713.771      0.0       0        0   9.892  1.174 152
# 164 1992 SYBN100 139.345   0.000   0.000     0.0   0.000 289.338 6028.138      0.0       0        0   2.401  1.056 164

ids <- 134 + c(1962, 1971, 1980, 1992) - 1962

# Measured SOC for No-till Corn-Soy rotation in Wooster, OH long-term experimental plot.
wooster_soc <- data.frame("year" = c(1962, 1971, 1980, 1992), id = ids, "measSOC" = c(3402, 4789.45, 3885, 4266.28))

# Plot SOC.
plot(x = wooster_lis$id, y = wooster_lis$somsc, type = 'l', lwd = 3, xlab = "", ylab = "SOC (g C/m^2)", ylim = c(0, 11000))
points(x = wooster_soc$id, y = wooster_soc$measSOC, pch = 16, col = "red")

#### 
unlink(dc_exe)
unlink(dc_L100)


