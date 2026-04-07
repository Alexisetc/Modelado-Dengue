source("/Users/joanponce/Desktop/FCA/FILES FOR JOAN/Libraries.R")
library(readxl)
library(zoo)

# Read the specific page from the Excel document
Data_Lita <- read.csv("/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/Data/INSPI_CZ9_GIDi_SIT_RLA5074_Field_2018-2019-2020-2021_20230503_DC_CM_FM_XAG.csv")

ae.AE<-data.frame(Date_collected = Data_Lita$Fecha.de.colecta.de.ovitrampa, Num_eggs = Data_Lita$Número.de.huevos.colectados..de.papel.de.ovitrampa., 
                  Num_alb = Data_Lita$Total.adultos.aedes.albopictus, Num_aeg = Data_Lita$Total.adultos.aedes.aegypti.1) 
ae.AE<-ae.AE[-1,]

# Sample data with dates in a single column
dates_column <- ae.AE$Date_collected
# Splitting the dates into three columns
date_parts <- do.call(rbind, strsplit(dates_column, "/"))
# Creating a data frame with the split columns
df <- data.frame(month = as.numeric(date_parts[,1]),
                 day = as.numeric(date_parts[,2]),
                 year = as.numeric(date_parts[,3]))
df$year <- paste0("20", df$year)

ae.AE<-cbind(df, ae.AE$Num_eggs, ae.AE$Num_aeg, ae.AE$Num_alb)

# Merge the three columns into a single column with a date format: date_col=date ovitrap was collected
ae.AE$date_col <- as.Date(paste(ae.AE$month, ae.AE$day, ae.AE$year, sep = "/"), format = "%m/%d/%Y")

ae.AE<-data.frame(
  date_col = ae.AE$date_col,
  Num_Eggs = as.numeric(ae.AE$`ae.AE$Num_eggs`),
  Num_aeg = as.numeric(ae.AE$`ae.AE$Num_aeg`),
  Num_alb = as.numeric(ae.AE$`ae.AE$Num_alb`)
)
ae.AE[is.na(ae.AE)] <- 0
# Aggregate the numbers by date
ae.AE <- aggregate(cbind(Num_Eggs, Num_aeg, Num_alb) ~ date_col, data = ae.AE, FUN = sum)

# Print the result
head(ae.AE)
#write_csv(ae.AE, "/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/Data/Mosquito counts/egg_larvae_counts.csv")


# Melt the dataframe to long format
library(ggplot2)
library(reshape2)
library(data.table)
df_long <- melt(ae.AE, id.vars = "date_col")

# Plot
mosquito_plot<-ggplot(df_long, aes(x = date_col, y = value, color = variable)) +
  geom_line() +
  labs(title = "Time Series Plot",
       x = "Date",
       y = "Value",
       color = "Variable") +
  theme_minimal()+
  scale_x_date(date_labels = "%b %Y")  # Format for month and year
  

first_detection_Alb <- ae.AE$Num_alb != 0
# Print the first row
if (!is.na(first_detection_Alb)) {
  print(ae.AE[first_detection_Alb, ])
} else {
  print("No row where values in col1 are different from 0.")
}

#rolling average
# Sample time series data (replace with your actual data)
num_eggs_vector <- ae.AE$Num_Eggs

#Add sum of larvaes of both species to the plot
ae.AE$sum_larvae<-ae.AE$Num_aeg+ae.AE$Num_alb

num_larvae_vector <- ae.AE$sum_larvae

# Define window size for rolling average
window_size <- 8

# Compute rolling average using base R functions
rolling_avg <- rollapply(num_eggs_vector, width = window_size, FUN = mean, align = "right", fill = NA)
rolling_avg_AE <- rollapply(ae.AE$Num_aeg, width = window_size, FUN = mean, align = "right", fill = NA)
rolling_avg_Alb <- rollapply(ae.AE$Num_alb, width = window_size, FUN = mean, align = "right", fill = NA)

# Add rolling average to the dataframe with NA padding to align
ae.AE$Rolling_Average <- c(rolling_avg, rep(NA, length(num_eggs_vector) - length(rolling_avg)))

# Melt the dataframe to long format
df_long <- melt(ae.AE, id.vars = "date_col")

# Plot
mosquito_plot <- ggplot(df_long, aes(x = date_col, y = value, color = variable)) +
  geom_line() +
  geom_line(data = ae.AE, aes(y = Rolling_Average), color = "red", linetype = "dashed", size = 1) +  # Add rolling average
  geom_line(data = ae.AE, aes(y = sum_larvae), color = "green", linetype = "dashed", size = 1) +  # Add 
  labs(title = "Time Series Plot with Rolling Average",
       x = "Date",
       y = "Value",
       color = "Variable") +
  theme_minimal() +
  scale_x_date(date_labels = "%b %Y")  # Format for month and year

# Show the plot
print(mosquito_plot)

# Plot
mosquito_plot_1 <- ggplot(df_long, aes(x = date_col, y = value, color = variable)) +
  geom_line() +
  geom_line(data = ae.AE, aes(y = Rolling_Average), color = "red", linetype = "dashed", size = 1) +  # Add rolling average
  geom_line(data = ae.AE, aes(y = sum_larvae), color = "green", linetype = "dashed", size = 1) +  # Add 
  labs(title = "Time Series Plot with Rolling Average",
       x = "Date",
       y = "Value",
       color = "Variable") +
  theme_minimal() +
  scale_x_date(date_labels = "%b %Y")  # Format for month and year
mosquito_plot_1





#Temperature data
#temp_daily_2018_2019.csv
temp_18_19_Lita<-as.data.frame(read_csv("/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/Data/temperatura Lita/temp data final/temp_daily_2018_2019.csv"))
temp_21_23_Lita<-as.data.frame(read_csv("/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/Data/temperatura Lita/temp data final/temp_daily_2021_2023.csv"))

temp_18_19_21_23<-rbind(temp_18_19_Lita, temp_21_23_Lita)
ae.AE_full<-merge(ae.AE, temp_18_19_21_23, by.x = "date_col", by.y = "temp_date", all.x = T)

ae.AE_full1<-ae.AE_full %>% dplyr::select(date_col, Num_Eggs,Num_aeg,Num_alb,Temp_daily)
# Plot
df_long1 <- melt(ae.AE_full1, id.vars = "date_col")
ggplot(df_long1, aes(x = date_col, y = value, color = variable)) +
  geom_line() +
  labs(title = "Time Series Plot",
       x = "Date",
       y = "Value",
       color = "Variable") +
  theme_minimal()+
  scale_x_date(date_labels = "%b %Y")  # Format for month and year
  
plot(ae.AE_full1$date_col ,ae.AE_full1$Temp_daily)


#Mosquito counts from 2023 and 2024

Data_Lita_23 <- read.csv("/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/Data/Mosquito_counts_23_24.csv")

aedes_counts_23<-data.frame(Date_collected = Data_Lita_23$Fecha.de.colecta.de.ovitrampa, Num_eggs = Data_Lita_23$Número.de.huevos.colectados..de.papel.de.ovitrampa...Sumatoria.de.enteros..rotos.y.no.viables., 
                  Num_alb = Data_Lita_23$emg_egg_lrv_aedes_alb, Num_aeg = Data_Lita_23$emg_egg_lrv_aedes_aeg)

aedes_counts_23<-aedes_counts_23[-c(1,2),]

# Sample data with dates in a single column
dates_col <- aedes_counts_23$Date_collected
# Splitting the dates into three columns
date_part <- do.call(rbind, strsplit(dates_col, "/"))
# Creating a data frame with the split columns
df1 <- data.frame(day = as.numeric(date_part[,1]),
                 month = as.numeric(date_part[,2]),
                 year = as.numeric(date_part[,3]))

ae_23<-cbind(df1, aedes_counts_23$Num_eggs, aedes_counts_23$Num_aeg, aedes_counts_23$Num_alb)

# Merge the three columns into a single column with a date format: date_col=date ovitrap was collected
ae_23$date_col <- as.Date(paste(ae_23$month, ae_23$day, ae_23$year, sep = "/"), format = "%m/%d/%Y")

ae_23<-data.frame(
  date_col = ae_23$date_col,
  Num_Eggs = as.numeric(ae_23$`aedes_counts_23$Num_eggs`),
  Num_aeg = as.numeric(ae_23$`aedes_counts_23$Num_aeg`),
  Num_alb = as.numeric(ae_23$`aedes_counts_23$Num_alb`)
)
ae_23[is.na(ae_23)] <- 0
# Aggregate the numbers by date
ae_23 <- aggregate(cbind(Num_Eggs, Num_aeg, Num_alb) ~ date_col, data = ae_23, FUN = sum)

# Melt the dataframe to long format
library(ggplot2)
library(reshape2)
library(data.table)
ae_23_long <- melt(ae_23, id.vars = "date_col")

# Plot
mosquito_plot2<-ggplot(ae_23_long, aes(x = date_col, y = value, color = variable)) +
  geom_line() +
  labs(title = "Time Series Plot",
       x = "Date",
       y = "Value",
       color = "Variable") +
  theme_minimal()+
  scale_x_date(date_labels = "%b %Y")  # Format for month and year

mosquito_plot2

