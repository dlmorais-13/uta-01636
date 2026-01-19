setwd("/home/daniel/Projects/daycent/sample/")

year_summary <- read.table(file = "year_summary.out", skip = 1)
names(year_summary) <- c("time", "N2Oflux", "NOflux", "N2flux", "NH3flux", "CH4_oxid", "NIT", "ANNPPT")
year_summary$TNflux <- rowSums(year_summary[,c("N2Oflux", "NOflux", "N2flux", "NH3flux")])

plot(x = year_summary$time, y = year_summary$N2Oflux, type = 'l', lwd = 3, xlab = "year", ylab = "N2Oflux", xlim = c(1900, 2100))
# plot(x = year_summary$time, y = year_summary$TNflux, type = 'l', lwd = 3, xlab = "year", ylab = "TNflux", xlim = c(1900, 2100))
