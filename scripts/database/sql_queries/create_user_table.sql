CREATE TABLE ${table_name} (
    User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    DummyJSON_ID INTEGER NOT NULL,
    First_Name VARCHAR(25) NOT NULL,
    Last_Name VARCHAR(25) NOT NULL,
    Age INTEGER NOT NULL,
    Gender VARCHAR(25) NOT NULL,
    Height DOUBLE NOT NULL,
    Weight DOUBLE NOT NULL,
    Latitude DOUBLE NOT NULL,
    Longitude DOUBLE NOT NULL,
    Country VARCHAR(25),
    Top_Product_Category VARCHAR(50)
)