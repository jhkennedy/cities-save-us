# For rendering the per-country emissions plot for our AGU poster
library('ggplot2')
library('grid')
library('ggthemes')
library('extrafont')


#  from https://rpubs.com/Koundy/71792
theme_Publication <- function(base_size=10, base_family="Helvetica") {
    library(grid)
    library(ggthemes)
    (theme_foundation(base_size=base_size, base_family=base_family)
        + theme(plot.title = element_text(face = "bold",
                                          size = rel(1.2), hjust = 0.5),
                text = element_text(),
                panel.background = element_rect(colour = NA),
                plot.background = element_rect(colour = NA),
                panel.border = element_rect(colour = NA),
                axis.title = element_text(face = "bold",size = rel(1)),
                axis.title.y = element_text(angle=90,vjust =2),
                axis.title.x = element_text(vjust = -0.2),
                axis.text = element_text(),
                axis.line = element_line(colour="black"),
                axis.ticks = element_line(),
                panel.grid.major = element_line(colour="#f0f0f0"),
                panel.grid.minor = element_blank(),
                legend.key = element_rect(colour = NA),
                legend.position = "bottom",
                legend.direction = "horizontal",
                legend.key.size= unit(0.2, "cm"),
                legend.spacing = unit(0, "cm"),
                legend.title = element_text(face="italic"),
                plot.margin=unit(c(10,5,5,5),"mm"),
                strip.background=element_rect(colour="#f0f0f0",fill="#f0f0f0"),
                strip.text = element_text(face="bold")
        ))
}

scale_fill_Publication <- function(...){
    library(scales)
    discrete_scale("fill","Publication",manual_pal(values = c("#386cb0","#fdb462","#7fc97f","#ef3b2c","#662506","#a6cee3","#fb9a99","#984ea3","#ffff33")), ...)
    
}

scale_colour_Publication <- function(...){
    library(scales)
    discrete_scale("colour","Publication",manual_pal(values = c("#386cb0","#fdb462","#7fc97f","#ef3b2c","#662506","#a6cee3","#fb9a99","#984ea3","#ffff33")), ...)
    
}


ca.data <- read.csv('CanadaLittleDataBook.csv',header=T)

# Let's get sane column names 
names(ca.data) <- c('Country','UrbPopPct2017','CO2EmisPerCapita2017', 'CO2EmisPerCountry2017')

g <- ggplot(data=ca.data, aes(get('UrbPopPct2017'), get('CO2EmisPerCapita2017'), size=CO2EmisPerCountry2017))
g + geom_point(color='red') + stat_smooth(method=lm) + geom_text(aes(label=Country),color='black',size=4, nudge_x=0.05, nudge_y=0.8) + ylab('CO2 Emissions\n (Metric Tonnes per Capita') + xlab('Urban Population (% of Total)') + labs(size="CO2 Emissions per Country (Metric Kilotonnes)") + scale_fill_Publication() + theme_Publication()

ggsave('emissions.pdf', width=5, height=5, units='in', device = cairo_pdf)


ggsave('emissions.pdf', device = cairo_pdf)
