#Install packages

#install.packages(c("plyr", "ggplot2","rgeos", "maptools","gpclib"))
install.packages('ggrepel')

#Load libraries
library(plyr)
library(rgeos)
library(maptools)
library(gpclib)
library(ggplot2)
library(magrittr)
library(dplyr)
library(tidyr)
library(ggrepel)


#Load data
data = readxl::read_excel("~/links/cn/data/processed/21_10_2017_ahrc_creative_cluster_data.xls",
                          sheet = 2)
#Drop irrelevant variables
data = data[,c(1:(length(names(data))-2))]

names(data)[c(2:length(names(data)))] = paste('y_',names(data)[c(2:length(names(data)))],sep = '')

#Create decile df

#with(data[,'y_2015_advertising_and_marketing_employment'],
#     cut(y_2015_advertising_and_marketing_employment,
#         breaks=quantile(y_2015_advertising_and_marketing_employment,
#                         probs=seq(0,1,by=0.5),na.rm = TRUE),
#                         include.lowest=TRUE))

#This is how you do it
data_long = data %>% gather(key='variable',value='value',-ttwa_name)

#Mutate
data_long = data_long %>%
  #Identify type of variable (LQ/total)
  mutate(measure_type=if_else(grepl('lq',variable)==TRUE,'lq','total'))%>%
  #Identify type of measure
  mutate(metric=if_else(grepl('employment',variable)==TRUE,'Employment',
                          'Business count')) %>%
  #Remove guff from variable names
  mutate(clean_name = gsub('y_2015||employment|business_counts|lq','',
                           variable)) %>%
  mutate(clean_name=gsub('^_|_$','',clean_name)) %>%
  mutate(clean_name=gsub("_"," ",clean_name)) %>%
  mutate(clean_name=trimws(clean_name))


#Now we have a tidy dataset to work with

#Load the shapefile
np_dist <- readShapeSpatial("~/links/cn/data/external/Travel_to_Work_Areas_December_2011_Full_Extent_Boundaries_in_United_Kingdom.shp")

#Fortity
np_dist <- fortify(np_dist, region = "ttwa11nm")

#Map theme
map_theme <- theme(
  panel.grid=element_blank(),
  axis.ticks=element_blank(),
  axis.text=element_blank(),
  axis.title=element_blank(),
  panel.background=element_rect(fill="white"),
  legend.position = 'bottom')

#Test
#Create centroids

ttwa_centroid = np_dist %>%
  group_by(id) %>%
  summarise(lat = mean(lat),lon=mean(long))

selected_centroids = ttwa_centroid[ttwa_centroid$id %in% selected_ttwas,]


#Functions for the maps
capitalise = function(x) {
  cap = paste(toupper(substr(x,1,1)),substr(x,2,nchar(x)),sep = '')
  return(cap)
}

#Create map
create_sector_map <- function(sector_name,deciles=FALSE) {
  ## x is the subsector we want to subset by
  
  #Filter data
  sector_data <-  filter(data_long,
                   measure_type=='lq',
                   clean_name==sector_name)
  
  #Get top TTWAs (for adding labels)
  top_ttwas <- filter(data_long,
                      measure_type=='total',
                      metric=='Business count',
                      clean_name==sector_name) %>%
    arrange(desc(value))
  
  selected_ttwas = top_ttwas$ttwa_name[c(1:10)]
  
  #Subset the centroids df
  selected_centroids = ttwa_centroid[ttwa_centroid$id %in% selected_ttwas,]
     
  #If we have decided to discretise the data?
  if (deciles==TRUE){
    spread_lqs = sector_data[,c('ttwa_name','metric','value')] %>% spread(metric,value,)
    
    #Discretise
    sector_data <-spread_lqs %>% 
      mutate(`Business count` = ntile(`Business count`,10),
             `Employment` = ntile(Employment,10)) %>%
      gather(key='metric',value='value',-ttwa_name)
    
  }
  
  
  map <- ggplot() + geom_map(data = sector_data, 
                             aes(map_id = ttwa_name,
                                 fill = value), 
                             color='grey50',size=0.001,
                             map = np_dist) + 
    expand_limits(x = np_dist$long, y = np_dist$lat) +
    #This adds the labels for the top 10 
    geom_point(data=selected_centroids,aes(x=lon,y=lat),size=1,color='black')+
    #Repel labels
    geom_label_repel(data=selected_centroids,aes(x=lon,y=lat,label=id),
                     fontface = 'bold', color = 'gray0',
                     fill='gold1',
                     box.padding = unit(0.35, "lines"),
                     point.padding = unit(0.5, "lines"),
                     segment.color = 'grey15',
                     size=1.2)+
    labs(title=capitalise(sector_name))+
    facet_wrap(~metric)+
    #Set scales based on whether we are mapping deciles or totals
    scale_fill_gradient2(
      low = "steelblue", mid = "white",high='coral',
      midpoint = ifelse(deciles==FALSE,1,5),
      name=ifelse(deciles==FALSE,'Location quotient','LQ decile'))+
    map_theme
  
  return(map)

}


#Get all maps done
pdf('~/links/cn/reports/figures/maps_totals.pdf',width = 6,height = 5)
for (var in unique(data_long$clean_name)) {
  print(var)
  if (var != 'not creative') {
    map <-  create_sector_map(var)
    print(map)
  }
}
dev.off()

#Deciles
pdf('~/links/cn/reports/figures/maps_deciles.pdf',width = 6,height = 5)
for (var in unique(data_long$clean_name)) {
  print(var)
  if (var != 'not creative') {
    map <-  create_sector_map(var,deciles = TRUE)
    print(map)
  }
}
dev.off()


#Add names
#Discretise
