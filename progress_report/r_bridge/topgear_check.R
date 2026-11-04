# Reproduces the TopGear MacroPCA example of the cellWise vignette "MacroPCA_examples"
# (code steps as in the installed vignette) and prints the quantities the vignette reports,
# so they can be compared with the vignette's printed output.
.libPaths(c(Sys.getenv("RLIB"), .libPaths()))
suppressPackageStartupMessages({ library(cellWise); library(robustHD) })
data(TopGear)
myTopGear <- TopGear
rownames(myTopGear) <- paste(myTopGear[, 1], myTopGear[, 2])
rownames(myTopGear)[165] <- "Mercedes-Benz G"
myTopGear <- myTopGear[, -31]
transTG <- myTopGear
for (v in c("Price", "Displacement", "BHP", "Torque", "TopSpeed")) transTG[[v]] <- log(myTopGear[[v]])
checkData <- checkDataSet(transTG, silent = TRUE)
remTG <- checkData$remX
num <- myTopGear[, sapply(myTopGear, is.numeric)]
cat("TopGear raw dim:", dim(TopGear), "\n")
cat("numeric columns in raw data:", ncol(num), " missing cells among them:", sum(is.na(num)), "\n")
cat("remTG dim:", dim(remTG), "\n")
MacroPCApars <- list(DDCpars = list(fastDDC = FALSE, silent = TRUE), scale = TRUE, silent = TRUE)
t0 <- Sys.time()
fit <- MacroPCA(transTG, k = 2, MacroPCApars = MacroPCApars)
cat("MacroPCA seconds:", round(as.numeric(Sys.time() - t0, units = "secs"), 2), "\n")
cat("cutoffOD:", format(fit$cutoffOD, digits = 7), "\n")
cat("cutoffSD:", format(fit$cutoffSD, digits = 7), "\n")
cat("flagged cells:", length(fit$indcells), "\n")
cat("cellWise version:", as.character(packageVersion("cellWise")), "\n")
