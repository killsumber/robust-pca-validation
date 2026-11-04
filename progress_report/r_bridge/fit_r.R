# Usage: Rscript fit_r.R <method: macropca|cellpca> <file_list.txt> <out_dir> [cellPCA_code.R]
# Reads each X csv (no header, n x p), fits q = 2 components, writes the p x 2 loadings
# to <out_dir>/<basename>_<method>.csv and the run time to <basename>_<method>.time.
# R is used as a black box: no R code is copied into the Python package.
.libPaths(c(Sys.getenv("RLIB"), .libPaths()))
suppressPackageStartupMessages(library(cellWise))
args <- commandArgs(trailingOnly = TRUE)
method <- args[1]; files <- readLines(args[2]); out_dir <- args[3]
if (method == "cellpca") {
  suppressPackageStartupMessages({ library(rrcov); library(RobStatTM) })
  source(args[4])  # authors' cellPCA code, downloaded from their software page
}
for (f in files) {
  base <- sub("\\.csv$", "", basename(f))
  out <- file.path(out_dir, paste0(base, "_", method, ".csv"))
  if (file.exists(out)) next
  X <- as.matrix(read.csv(f, header = FALSE))
  t0 <- Sys.time()
  V <- tryCatch({
    if (method == "macropca") {
      # scale = FALSE: the true subspace refers to the unscaled covariance
      MacroPCA(X, k = 2, MacroPCApars = list(scale = FALSE, silent = TRUE))$loadings[, 1:2]
    } else {
      cellPCA(X, q = 2, trace = FALSE)$V[, 1:2]
    }
  }, error = function(e) { writeLines(conditionMessage(e), file.path(out_dir, paste0(base, "_", method, ".err"))); NULL })
  if (!is.null(V)) {
    write.table(V, out, sep = ",", row.names = FALSE, col.names = FALSE)
    writeLines(format(as.numeric(Sys.time() - t0, units = "secs")), file.path(out_dir, paste0(base, "_", method, ".time")))
  }
}
