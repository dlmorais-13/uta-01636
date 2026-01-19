setwd("/home/daniel/Projects/daycent/sample/")

wooster_lis <- read.table(file = "wooster.lis", skip = 3)
names(wooster_lis) <-  c("time", "crpval", "cgrain", "accrst", "agcprd", "bgcjprd", "bgcmprd",
					"cinput", "somsc", "fertot11", "omadtot", "omaetot1", "strmac2", "volpac")
# wooster_lis$id <- 1:nrow(wooster_lis)

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

# ids <- 134 + c(1962, 1971, 1980, 1992) - 1962

# Measured SOC for No-till Corn-Soy rotation in Wooster, OH long-term experimental plot.
# wooster_soc <- data.frame("year" = c(1962, 1971, 1980, 1992), id = ids, "measSOC" = c(3402, 4789.45, 3885, 4266.28))

# Plot SOC.
plot(x = wooster_lis$time, y = wooster_lis$somsc, type = 'l', lwd = 3, xlab = "year", ylab = "SOC (g C/m^2)", ylim = c(0, 11000), xlim = c(1900, 2100))
# points(x = wooster_soc$id, y = wooster_soc$measSOC, pch = 16, col = "red")
# plot(x = wooster_lis$id, y = wooster_lis$somsc, type = 'l', lwd = 3, xlab = "", ylab = "SOC (g C/m^2)", ylim = c(0, 11000))
# points(x = wooster_soc$id, y = wooster_soc$measSOC, pch = 16, col = "red")
