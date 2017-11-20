library(dplyr)
library(tidyr)
library(magrittr)


#'Back of the envelope' calculation for Hasan
geo_data <- read.csv("/Users/jmateosgarcia/Downloads/geo_creativity_data.csv",encoding = 'latin1')

#Activities
#Top 8 places

#Sort and extract
top_geo <- geo_data %>% arrange(desc(X2014_All.creative.industries_turnover))
top_ttwas <- top_geo[1:9,'TTWA']

#Variables of interest
econ_perf <- c("X2007_All.creative.industries_turnover",
               "X2014_All.creative.industries_turnover",
               "X2007_All.creative.industries_employment",
               "X2014_All.creative.industries_employment",
               "Creative.GVA..Î.GBP.")


#Growth rates
#Subset
rel_data = geo_data[,c("TTWA",'region',econ_perf)]

rel_data <- rel_data %>% rename(ttwa=TTWA,
                                turn_2007=X2007_All.creative.industries_turnover,
                                turn_2014=X2014_All.creative.industries_turnover,
                                emp_2007=X2007_All.creative.industries_employment,
                                emp_2014=X2014_All.creative.industries_employment,
                                gva_2014=Creative.GVA..Î.GBP.) %>%
  mutate(turn_growth=turn_2014/turn_2007,
         emp_growth = emp_2014/emp_2007,
         london_se = ifelse(region %in% c("London","South East"),
                            TRUE,FALSE))

#Produce South East estimate
south_east <- rel_data %>%
  filter(!is.na(turn_2007) & !is.na(turn_2007)) %>%
  summarise(turn_reg_2007=sum(turn_2007),
            turn_reg_2014 = sum(turn_2014)) %>%
  mutate(turn_growth=turn_reg_2014/turn_reg_2007)

#Produce Non-south east figures
#Get top non-London / SE areas
top_not_se <- rel_data %>% filter(london_se==FALSE) %>% arrange(desc(emp_2014))
north_top <- top_not_se[1:8,'ttwa']
nort_stats <- rel_data[rel_data$ttwa %in% north_top,]

south_east <- geo_data %>% mutate(london_se = ifelse(region %in% c("London","South East"),
                    TRUE,FALSE)) %>% group_by(london_se)
                    
#Arbitrary improvement
growth_estimate <- rel_data %>% filter(ttwa %in% north_top & london_se == FALSE) %>% 
  mutate(growth_uplift=1.1,
    new_growth_rate= emp_growth*growth_uplift,
    new_gva_w_programme_thGBP = new_growth_rate*gva_2014,
    new_gva_baseline_thGBP = emp_growth*gva_2014) %>%
  select(ttwa,region,emp_2007,emp_2014,emp_growth,growth_uplift,new_growth_rate,gva_2014,
         new_gva_w_programme_thGBP,new_gva_baseline_thGBP)

growth_estimate_2 <- rel_data %>% filter(ttwa %in% north_top & london_se == FALSE) %>% 
  select(ttwa,region,emp_2007,emp_2014,gva_2014)

growth_aggs <- as.data.frame(t(colSums(growth_estimate_2[,c(3:length(names(growth_estimate_2)))])))
growth_aggs['emp_growth'] <-  growth_aggs['emp_2014']/growth_aggs['emp_2007']


growth_aggs$growth_upscale <- 1.1
growth_aggs$growth_programme <- growth_aggs$growth_upscale * growth_aggs$emp_growth


growth_aggs$gva_2021_programme <- growth_aggs$growth_programme * growth_aggs$gva_2014
growth_aggs$gva_2021_baseline <- growth_aggs$emp_growth * growth_aggs$gva_2014

growth_aggs$gva_2021_impact <- growth_aggs$gva_2021_programme - growth_aggs$gva_2021_baseline

growth_aggs$gva_growth_baseline_pa <- 100*((growth_aggs$emp_growth-1)/7)
growth_aggs$gva_growth_programme_pa <- 100*((growth_aggs$growth_programme-1)/7)

write.csv(growth_aggs,'~/links/cn/data/interim/growth_estimate_25oct2017.csv')

for (x in list(north_top)) {
  print(x)
}
