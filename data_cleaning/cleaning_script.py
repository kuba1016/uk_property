import pandas as pd

# load data
df = pd.read_csv("../data/data.csv")

# data check
print(df.head())
print(df.info())

# droping NA
df.dropna(inplace=True)

# cleaning price column
df.drop(df[df.price=="price"].index,inplace = True)
df.drop(df[df.price=="POA"].index,inplace = True)
df.price =df.price.str.replace("£","").str.replace(",","").astype(int)

# cleaning beds column
df.beds = df.beds.str.replace(r"\D","").astype(int)
df.loc[df.beds > 5,"more_tan_5"] = True
df.drop(df[df.more_tan_5 ==True].index, inplace = True)

# cleaning baths column
df.baths = df.baths.str.replace(r"\D","").astype(int)
df.loc[df.baths > 4,"more_than_4_baths"] = True
df.drop(df[df.more_than_4_baths ==True].index, inplace = True)

# cleaning receptions column
df.receptions=df.receptions.str.replace(r"\D","").astype(int)
df.loc[df.receptions > 3, "more_than_3_recep"] = True
df.drop(df[df.more_than_3_recep == True].index, inplace=True)

# creating post_code column
df["post_code"] = df.address.str.extract(r"([A-Z]{1,2}[0-9]{1,2})")

# selecting final shape of def
df =df.loc[:,["agent","address","beds","receptions","baths","post_code"]]

print(df.head())
print(df.info())

df.to_csv("../data/clean_data.csv")
