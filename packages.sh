#! /usr/bin/env bash

Packages=(
base
data.table
devtools
doParallel
dplyr
foreach
ggplot2
graphics
grDevices
httr
knitr
MASS
Matrix
methods
plyr
reshape2
stats
utils
)

for pkg in "${Packages[@]}"
do
    Rscript packages.R $pkg
done
