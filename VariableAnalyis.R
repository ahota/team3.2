setwd("~/Documents/Class/Grad/2014Fall/FDAC/team3.2")

# Read in dataframe that the list of users that have contributed
# to other projects (not their own) (note: sample of 1 million)
df <- read.table("contribNotOwner_1million.txt", sep=':', head=F)
attach(df)
options(scipen=999)
summary(V2)
hist(V2)

# A log transformation, but it will just show the same distribution.
l <- log10(V2)
summary(l)

# Plotting the histogram and density
# Really shows how bad the distribution is.
# Can barely see the density plot because it looks likes the axis.

hist(l)
d <- density(V2)
plot(d)
quantile(V2, c(.01, .25, .50, .75, .85, .90, .95, .99))

library(fBasics)
basicStats(V2)
detach(df)
options(gsubfn.engine = "R")
require("sqldf")
no1s <- sqldf("select * from df where V2>1")
nrow(no1s)

# Skewness is a measure of symmetry,
# or rather, lack thereof. We define
# symmetry if the distribution looks the
# same to the left and right of the center value.
# The Skewness of a normal distribution is 0.

# Kurtosis is a measure of whether the data are
# peaked or flat relative to a normal distribution.
# Datasets with low kurtosis would have a flat top
# near the mean (a uniform distribution being the extreme).
# A high kurtosis would have a high peak near the mean,
# decline rapidly, and have long tails. The kurtosis for
# a standard normal distribution is 3.
# The "basicStats" function uses an alternate definition
# of kurtosis ("excess kurtosis) where the value for a normal distribution is 0,
# and a positive value indicates a "peaked" distribution and
# a negative value indicates a "flat" distribution.

# No matter how you want to transform this data,
# none will sufficiently work, since the data is
# discrete and more than 85% of the data is the
# same value. Therefore, no matter what transform you use,
# that 85% will still be the same value.

# Read in dataframe that the list of users that have contributed
# to projects (including their own) (note: sample of 1 million)
df2 <- read.table("contrib_one_million.txt", sep=':', head=F)
attach(df2)
options(scipen=999)
summary(V2)
hist(V2)
l <- log10(V2)
summary(l)
hist(l)

quantile(V2, c(.01, .25, .50, .75, .85, .90, .95, .99))
library(fBasics)
basicStats(V2)
d <- density(V2)
plot(d)

# Note the differences in Skewness and Kurtosis.
# This sample is "better", but still nowhere
# near an appropriate variable to use as a predictor.

# The only variables that will correlate with these two
# variables are ones that have a majority of the data as
# one value (probably discrete sets).
# Thus, the only "relationship" that correlation will be looking
# for is this one- an extrememly strong unimodal yet asymmetic
# distribution (as opposed to an actual relationship).




