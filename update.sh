#! /usr/bin/env bash

Packages=(
base
boot
car
caret
data.table
devtools
doParallel
dplyr
foreach
ggplot2
glmnet
graphics
grDevices
htmlwidgets
httr
jsonlite
knitr
lme4
MASS
Matrix
methods
mgcv
nlme
parallel
plyr
randomForest
Rcpp
reshape2
shiny
stats
stringr
survival
testthat
utils
)

for pkg in "${Packages[@]}"
do
    Rscript packages.R $pkg
done

Rscript syntax.R
