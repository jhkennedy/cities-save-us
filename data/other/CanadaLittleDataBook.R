# For rendering the per-country emissions plot for our AGU poster
library(ggplot2)

# The default fonts are usually tiny, so buff 'em up a bit.
theme_set(theme_gray(base_size = 11))

ca.data <- read.csv('CanadaLittleDataBook.csv',header=T)

# Let's get sane column names 
names(ca.data) <- c('Country','UrbPopPct2017','CO2EmisPerCapita2017', 'CO2EmisPerCountry2017')

g <- ggplot(data=ca.data, aes(get('UrbPopPct2017'), get('CO2EmisPerCapita2017'), size=CO2EmisPerCountry2017))
g + geom_text(aes(label=Country),size=4) + geom_point() + ylab('CO2 Emissions\n (Metric Tonnes per Capita') + xlab('Urban Population (% of Total)')
