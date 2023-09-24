#!/usr/bin/env python
# coding: utf-8

# <h2 align="center">AtliQ Hotels Data Analysis Project<h2>

# In[1]:


import pandas as pd


# ### ==> 1. Data Import and Data Exploration

# ### Datasets
# We have 5 csv file 
# 
#    - dim_date.csv  
#    - dim_hotels.csv
#    - dim_rooms.csv
#    - fact_aggregated_bookings
#    - fact_bookings.csv

# In[2]:


df_bookings = pd.read_csv("datasets/fact_bookings.csv")
df_bookings.head(4)


# In[3]:


#check rows and colums
df_bookings.shape 


# In[4]:


#check unique room categories
#It has total 4 unique room categories
df_bookings.room_category.unique()


# In[5]:


#check unique book platforms
#It has total 7 unique book platforms
df_bookings.booking_platform.unique()


# In[6]:


#shows how many bookings are made per platform
df_bookings.booking_platform.value_counts()


# In[7]:


#making the count of booking in each platforms more visible and clear
df_bookings.booking_platform.value_counts().plot(kind = "barh")


# In[8]:


#shows overall statistics of data frame
#min value for no_guests is -17, which is very strange
#This weird values will be explored and fixed during data cleaning process
df_bookings.describe()


# In[9]:


#This is when I want to see the exact amount of specific data points
df_bookings.revenue_generated.min(),df_bookings.revenue_generated.max()


# In[10]:


#Now,loading remaining csv files 
df_date = pd.read_csv('datasets/dim_date.csv')
df_hotels = pd.read_csv('datasets/dim_hotels.csv')
df_rooms = pd.read_csv('datasets/dim_rooms.csv')
df_agg_bookings = pd.read_csv('datasets/fact_aggregated_bookings.csv')


# In[11]:


df_hotels.shape


# In[12]:


df_hotels.head(4)


# In[13]:


df_hotels.category.value_counts()


# In[14]:


df_hotels.city.value_counts().sort_values().plot(kind="bar")


# In[15]:


df_agg_bookings.head(3)


# In[16]:


#Find out unique property ids in aggregate bookings dataset
df_agg_bookings.property_id.unique()


# In[17]:


#Find out total bookings per property_id
df_agg_bookings.groupby("property_id")["successful_bookings"].sum()


# In[18]:


#Find out days on which bookings are greater than capacity
df_agg_bookings[df_agg_bookings.successful_bookings > 
                df_agg_bookings.capacity]


# In[19]:


#Find out properties that have highest capacity
df_agg_bookings.capacity.max()


# In[20]:


df_agg_bookings[df_agg_bookings.capacity == 
                df_agg_bookings.capacity.max()]


# ### ==> 2. Data Cleaning

# In[21]:


#figuring out strange values in the data frame
df_bookings.describe()


# In[22]:


#finding data that has guest number below 0
df_bookings[df_bookings.no_guests <= 0]


# In[23]:


#This gives the insight that I have so much data rows in the data frame
#that I can ignore the 12 rows above 
df_bookings.shape


# In[24]:


#check that 12 rows with negative guest numbers are eliminated from previous data frame
df_bookings = df_bookings[df_bookings.no_guests > 0]
df_bookings.shape


# In[25]:


#It is also suspicious that a single booking has huge revenue
df_bookings.revenue_generated.min(), df_bookings.revenue_generated.max() 


# In[26]:


avg, std = df_bookings.revenue_generated.mean(), df_bookings.revenue_generated.std()
avg, std


# In[27]:


higher_limit = avg + 3*std
higher_limit


# In[28]:


lower_limit = avg - 3*std
lower_limit


# In[29]:


df_bookings[df_bookings.revenue_generated > higher_limit]


# In[30]:


#getting rid of outliers using 3 standard deviation method
df_bookings = df_bookings[df_bookings.revenue_generated < higher_limit]
df_bookings.shape


# In[31]:


df_bookings.revenue_realized.describe()


# In[32]:


#this time, just checking if our maximum is to big to be considered as outliers
#however, as of 2023, paying 45000 in a single night seems possible
higher_limit = df_bookings.revenue_realized.mean() + 3*df_bookings.revenue_realized.std()
higher_limit


# In[33]:


#looks like there are too many outliers
#especially when room category is RT4
df_bookings[df_bookings.revenue_realized > higher_limit]


# In[34]:


df_rooms


# In[35]:


df_bookings[df_bookings.room_category == "RT4"].revenue_realized.describe()


# In[36]:


#this explains that we have nothing to clean for revenue realized value
23439 + 3*9048.6


# In[37]:


#It is okay for rating_given to have null values since people usually
#do not write ratings everytime they stay in hotel
df_bookings.isnull().sum()


# In[38]:


#In aggregate bookings find columns that have null values
df_agg_bookings.isnull().sum()
df_agg_bookings[df_agg_bookings.capacity.isna()]


# In[39]:


#finding median values that will replace the null
df_agg_bookings.capacity.median()


# In[40]:


#Filling out the null values with median and check if that worked
df_agg_bookings.capacity.fillna(df_agg_bookings.capacity.median(), inplace = True)
df_agg_bookings.loc[[8,14]]


# In[41]:


#finding out records that have successful_bookings value greater than capacity
df_agg_bookings[df_agg_bookings.successful_bookings > df_agg_bookings.capacity]


# In[42]:


df_agg_bookings.shape


# In[43]:


#checking if the adjustment has been successfully made
df_agg_bookings = df_agg_bookings[df_agg_bookings.successful_bookings <= df_agg_bookings.capacity]
df_agg_bookings.shape


# ### ==> 3. Data Transformation

# In[44]:


df_agg_bookings.head()


# In[45]:


#creating a new column is one of the data transformations
df_agg_bookings["occ_pct"] = df_agg_bookings["successful_bookings"] / df_agg_bookings["capacity"]
df_agg_bookings.head()


# In[46]:


#easy way of getting occupancy percentage using function as lambda
#This metric is useful especially in hotel business
df_agg_bookings["occ_pct"] = df_agg_bookings["occ_pct"].apply(lambda x: round(x*100, 2))
df_agg_bookings.head(4)


# ### ==> 4. Insights Generation

# **1. What is an average occupancy rate in each of the room categories?**

# In[47]:


df_agg_bookings.groupby("room_category")["occ_pct"].mean().round(2)


# In[48]:


df_rooms


# In[49]:


#merging two tables to replace the room_id with specific room class
df = pd.merge(df_agg_bookings, df_rooms, left_on = "room_category", right_on = "room_id")
df.tail(4)


# In[50]:


#shows that the average occupancy percentage for each room types are around
#58.5 percent. Also, the presidential is the most favorite choice of people
df.groupby("room_class")["occ_pct"].mean().round(2)


# In[51]:


df.drop("room_id", axis=1, inplace=True)
df.head(4)


# **2. Print average occupancy rate per city**

# In[52]:


df_hotels.head(3)


# In[53]:


df = pd.merge(df, df_hotels, on="property_id")
df.head(3)


# In[54]:


df.groupby("city")["occ_pct"].mean().round(2).plot(kind="barh")


# **3. When was the occupancy better? Weekday or Weekend?**

# In[55]:


df.head(3)


# In[56]:


df = pd.merge(df, df_date, left_on="check_in_date", right_on="date")
df.head(3)


# In[57]:


#shows that people tend to book a room during weekend than weekday
df.groupby("day_type")["occ_pct"].mean().round(2)


# **4: In the month of June, what is the occupancy for different cities**

# In[58]:


df["mmm yy"].unique()


# In[59]:


df_june_22 = df[df["mmm yy"]=="Jun 22"]
df_june_22.head(3)


# In[60]:


#In june, Delhi is doing the best in occupancy percentage
df_june_22.groupby("city")["occ_pct"].mean().round(2).sort_values(ascending = False).plot(kind="bar")


# **5: We got new data for the month of august. Append that to existing data**

# In[61]:


#what if there is new dataset for August?
df_august = pd.read_csv("datasets/new_data_august.csv")
df_august.head(3)


# In[62]:


df_august.columns


# In[63]:


df.columns


# In[64]:


df_august.shape


# In[65]:


df.shape


# In[66]:


#axis = 0 means, I am concatenating the new data frame as row-wise
latest_df = pd.concat([df, df_august], ignore_index=True, axis=0)
latest_df.tail(10)


# In[67]:


latest_df.shape


# **6. Print revenue realized per city**

# In[68]:


df_bookings.head(4)


# In[69]:


df_hotels.head(3)


# In[70]:


df_bookings_all = pd.merge(df_bookings, df_hotels, on="property_id")
df_bookings_all.head(3)


# In[71]:


df_bookings_all.groupby("city")["revenue_realized"].sum()


# **7. Print month by month revenue**

# In[72]:


df_bookings_all.head(3)


# In[73]:


df_date["mmm yy"].unique()


# In[74]:


df_date.head(3)


# In[75]:


df_bookings_all.info()


# In[76]:


df_date.info()


# In[77]:


df_date["date"] = pd.to_datetime(df_date["date"])
df_date.head(3)


# In[78]:


df_date.info()


# In[79]:


df_bookings_all["check_in_date"] = pd.to_datetime(df_bookings_all["check_in_date"])
df_bookings_all.head(4)


# In[80]:


df_bookings_all.info()


# In[81]:


df_bookings_all = pd.merge(df_bookings_all, df_date, left_on='check_in_date', right_on="date")
df_bookings_all.head(3)


# In[82]:


#hotel made the most revenue during May in 2022
df_bookings_all.groupby("mmm yy")["revenue_realized"].sum()


# In[83]:


#revenue realized per hotel type
df_bookings_all.groupby('property_name')["revenue_realized"].sum().sort_values()


# In[84]:


#average rating per city
df_bookings_all.groupby("city")["ratings_given"].mean().round(2)


# In[85]:


#making a pie chart of revenue realized per booking platform
df_bookings_all.groupby("booking_platform")["revenue_realized"].sum().plot(kind="pie")

