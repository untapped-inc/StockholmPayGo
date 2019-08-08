CREATE TABLE "ORP" (
    "ReadingID" string  NOT NULL ,
    "Millivolts" int  NOT NULL ,
    "Timestamp" int  NOT NULL ,
    "DeviceID" string  NOT NULL ,
    -- synced with a remote server?
    "IsSynced" boolean  NOT NULL DEFAULT (0),
    CONSTRAINT "pk_ORP" PRIMARY KEY (
        "ReadingID"
    ),
    FOREIGN KEY (DeviceID) REFERENCES Device(DeviceID)
)

GO

-- This table stores a log of the water that was detected by the flowmeter
CREATE TABLE "WaterLog" (
    "FlowmeterReadingID" int  NOT NULL ,
    "DeviceID" string  NOT NULL ,
    "Timestamp" int  NOT NULL ,
    --amount of water that was measured through the flowmeter
    "Value" real NOT NULL,
    "Units" string NOT NULL,
    CONSTRAINT "pk_WaterLog" PRIMARY KEY (
        "FlowmeterReadingID"
    ),
    FOREIGN KEY (DeviceID) REFERENCES Device(DeviceID)

)

GO

-- This table stores the TDS readings
CREATE TABLE "TDS" (
    "TDSReadingID" int  NOT NULL ,
    "Millivolts" int  NOT NULL ,
    "Timestamp" int  NOT NULL ,
    "DeviceID" string  NOT NULL ,
    "IsSynced" boolean  NOT NULL DEFAULT (0),
    CONSTRAINT "pk_TDS" PRIMARY KEY (
        "TDSReadingID"
    ),
    FOREIGN KEY (DeviceID) REFERENCES Device(DeviceID)
)

GO

CREATE TABLE "Device" (
    -- allows for multiple users on one device FK >- HalfLiters.DeviceID
    "DeviceID" string  NOT NULL ,
    --price in USD per ml of water
    "PricePerML" real NOT NULL,
    -- the last time a GET request retrieved data from the remote server
    "LastDownSyncTime" int  NULLABLE ,
    -- the last time a POST request sent data to the server
    "LastUpSyncTime" int  NULLABLE ,
    CONSTRAINT "pk_Device" PRIMARY KEY (
        "DeviceID"
    )
)

GO

-- table to track the change in credits over time
CREATE TABLE "CreditAuditLog" (
    "CreditID" string  NOT NULL ,
    "CreditBalance" real  NOT NULL DEFAULT (0),
    "DeviceID" string  NOT NULL ,
    "Timestamp" int  NULL ,
    CONSTRAINT "pk_CreditAuditLog" PRIMARY KEY (
        "CreditID"
    ),
    FOREIGN KEY (DeviceID) REFERENCES Device(DeviceID)
)

GO
