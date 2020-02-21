installedPackages <- installed.packages()
packages <- installedPackages[, c(1)]
packagesString <- paste(packages, collapse=",")
packagesString