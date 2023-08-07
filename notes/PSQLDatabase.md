
# Introduction

Ideas for loading a database from TotalDepth data.

NOTE: At the moment this is very LIS specific.

# LIS

Schema: `lis`

Primary table is the `lis.file` which just associates a key with a particular physical file.
Within each LIS file are a number of log passes.
Within a log pass is a set of tables.

## File Table

Table: `lis.file`

### Columns

- `file_id` - Auto-generated primary key.
- `file_path` - File path.  Absolute, relative?

```sql
CREATE TABLE file (
  file_id               INT GENERATED ALWAYS AS IDENTITY,
  file_path             TEXT NOT NULL,
  PRIMARY KEY(file_id)
);
```

## Log Pass Table

Table: `lis.log_pass`

### Columns

- `log_pass_id` - Auto-generated primary key.
- `file_id` - Foreign key to `lis.file.file_id`
- `log_pass_index` - Index of the Log Pass in the file starting from 0.

```sql
CREATE TABLE log_pass (
  log_pass_id           INT GENERATED ALWAYS AS IDENTITY,
  file_id               INT,
  PRIMARY KEY(log_pass_id),
  CONSTRAINT fk_file
    FOREIGN KEY(file_id) 
    REFERENCES file(file_id)
  -- Unique columns in this table
  log_pass_index        INT NOT NULL,
);
```

## LIS File Header Table

Also reel and tape header, or do we really care about these?

NOTE: Ignore file trailer. Or raise if different?

Table: `lis.file_header`

### Columns

- `id` - Auto-generated primary key.
- `log_pass_id` - Foreign key to `lis.log_pass.log_pass_id`
- TODO:

```sql
CREATE TABLE file_header (
  id                INT GENERATED ALWAYS AS IDENTITY,
  log_pass_id                   INT,
  PRIMARY KEY(id),
  CONSTRAINT fk_log_pass
    FOREIGN KEY(log_pass_id) 
    REFERENCES log_pass(log_pass_id),
  -- Unique columns in this table
  file_name                     VARCHAR(10) NOT NULL,
  service_sub_level             VARCHAR(6) NOT NULL,
  version                       VARCHAR(8) NOT NULL,
  date                          VARCHAR(8) NOT NULL,
  max_physical_record_length    VARCHAR(5) NOT NULL,
  file_type                     VARCHAR(2) NOT NULL,
  previous_file_name            VARCHAR(10) NOT NULL,
  -- Calculated with Y2K considerations.
  date_computed                 DATE NOT NULL,
);
```

### TOOL Table

Table: `lis.tool`

### Columns

- `log_pass_id` - Auto-generated primary key.
- `file_id` - Foreign key to `lis.file.file_id`
- `log_pass_index` - Index of the Log Pass in the file starting from 0.

```sql
CREATE TABLE log_pass (
  tool_id               INT GENERATED ALWAYS AS IDENTITY,
  log_pass_id           INT,
  PRIMARY KEY(tool_id),
  CONSTRAINT fk_log_pass
    FOREIGN KEY(log_pass_id) 
    REFERENCES log_pass(log_pass_id),
  -- Unique columns in this table
  -- MNEM	STAT	LENG	WEIG	HEIG
  mnem                  VARCHAR(4) NOT NULL,
  stat                  BOOLEAN NOT NULL,
  -- Could be an integer though
  leng                  DOUBLE PRECISION NOT NULL,
  weig                  DOUBLE PRECISION NOT NULL,
  heig                  DOUBLE PRECISION NOT NULL,
);
```


TODO: INPU, OUTP, CONS, PRES, FILM, AREA, SONI?, CURV?

## `CONS` Table

There can be many `CONS` tables in a Log Pass.
The are assumed to be additive, or last row wins.

Columns: Typically:

$ tdlistablehistogram ~/dev/lis/pylis/data/ --name=CONS -s

defaultdict(<class 'int'>,
            {(34, b'CONS', b'ALLO'): 1012,
             (34, b'CONS', b'DESC'): 185,
             (34, b'CONS', b'MNEM'): 1197,
             (34, b'CONS', b'PUNI'): 1197,
             (34, b'CONS', b'STAT'): 185,
             (34, b'CONS', b'TUNI'): 1197,
             (34, b'CONS', b'VALU'): 1197})

Also DEFI, the explanation?

VALU has a value and a units (a MNEM).

### Columns

- `id` - Auto-generated primary key.
- `log_pass_id` - Foreign key to `lis.log_pass.log_pass_id`
- TODO:

```sql
CREATE TABLE cons (
  id                INT GENERATED ALWAYS AS IDENTITY,
  log_pass_id                   INT,
  PRIMARY KEY(id),
  CONSTRAINT fk_log_pass
    FOREIGN KEY(log_pass_id) 
    REFERENCES log_pass(log_pass_id),
  -- Unique columns in this table
  mnem                          VARCHAR(4) NOT NULL,
  stat                          BOOLEAN NOT NULL,
  allo                          BOOLEAN NOT NULL,
  puni                          VARCHAR(4) NOT NULL,
  tuni                          VARCHAR(4) NOT NULL,
  -- Could be an integer though.
  -- Can be null.
  valu                          DOUBLE PRECISION,
  desc                          TEXT,
  defi                          TEXT,
);
```

## DFSR

This consists of several tables:

- Frame information (length, number of channels). This is fixed format from the entry blocks. There are 16 columns starting with EB_TYPE_DATA_TYPE at src/TotalDepth/LIS/core/LogiRec.py:1261
- Channels, one row per channel with: Name, Service ID, Service Order, Units, API, File, Size, Rep Code, Sub-channels, Values per frame, Shape((sc, sa, bu),)
- X axis information (from, to, number of frames, units)
- Then actual data from looking at all the channels:
  - X axis information (min/mean/median/max spacing, back, duplicate, normal, skipped)
  - Log pass statistics ('frame data').

Question: For the dbase do we insist on everything NOT NULL and impose defaults,
or, set NULL in the dbase where absent an impose a default afterwards.
Or have separate table of default values?

### DFRS Entry Blocks

Fixed format table, one row per DFSR ('Log Pass').

```sql
CREATE TABLE dfsr_entry_blocks (
  id                            INT GENERATED ALWAYS AS IDENTITY,
  log_pass_id                   INT,
  PRIMARY KEY(id),
  CONSTRAINT fk_log_pass
    FOREIGN KEY(log_pass_id) 
    REFERENCES log_pass(log_pass_id),
  -- Unique columns in this table
  -- Default 0
  eb_type_data_type             INT NOT NULL,
  -- Default 0
  eb_type_dsb_type              INT NOT NULL,
  -- Must be present.
  eb_type_frame_size            INT NOT NULL,
  -- Default 1
  eb_type_up_down_flag          INT NOT NULL,
  -- Default 1
  eb_type_optical_depth_units   INT NOT NULL,
  eb_type_ref_point             INT,
  eb_type_ref_point_units       VARCHAR(4) NOT NULL,
  eb_type_frame_space           INT NOT NULL,
  eb_type_frame_space_units     VARCHAR(4) NOT NULL,
  eb_type_undefined_10          INT,
  eb_type_max_frames_per_rec    INT,
  -- Default -999.25
  eb_type_absent_value          DOUBLE PRECISION NOT NULL,
  -- Default 0
  eb_type_record_mode           INT NOT NULL,
  -- Default '0.1IN'
  eb_type_depth_units           VARCHAR(4) NOT NULL,
  eb_type_depth_rep_code        INT NOT NULL,
  eb_type_dsb_sub_type          INT NOT NULL,
);
```

### DFRS Channels

Multi row per DFSR ('Log Pass'). One row per channel.

Struct: '>4s 6s 8s 4s I 2h 3x 2B5x'

- Name: MNEM
- Service ID
- Service Order
- Units
- API
- File
- Size
- Rep Code
- Derived:
  - Sub-channels
  - Values per frame
  - Shape ((sc, sa, bu),)

```sql
CREATE TABLE dfsr_channels (
  id                            INT GENERATED ALWAYS AS IDENTITY,
  log_pass_id                   INT,
  PRIMARY KEY(id),
  CONSTRAINT fk_log_pass
    FOREIGN KEY(log_pass_id) 
    REFERENCES log_pass(log_pass_id),
  name                          VARCHAR(4) NOT NULL,
  service_id                    VARCHAR(6) NOT NULL,
  service_order                 VARCHAR(8) NOT NULL,
  units                         VARCHAR(4) NOT NULL,
  -- NOTE: 32 bit int that is divided into 4our sub-fields.
  api                           INT NOT NULL,
  file                          INT NOT NULL,
  size                          INT NOT NULL,
  rep_code                      INT NOT NULL,
  -- TODO: Derived, see TotalDepth.LIS.core.LogiRec.DatumSpecBlock._setBurstsSubChannels()
  sub_channels                  INT NOT NULL,
  values_per_frame              INT NOT NULL,
  -- TODO: Derived data, ((sc, sa, bu),)
  shape                         {{INT, INT, INT,},} NOT NULL,
);
```

## Essential Log Pass Data

Data taken from several tables but mainly the `CONS` tables.

### Table Name

`lis.well_log_pass`

### Columns

- `id` - Auto-generated primary key.
- `log_pass_id` - Foreign key to `lis.log_pass.log_pass_id`
- TODO.




```sql
CREATE TABLE well_log_pass (
  id                INT GENERATED ALWAYS AS IDENTITY,
  log_pass_id                   INT,
  PRIMARY KEY(id),
  CONSTRAINT fk_log_pass
    FOREIGN KEY(log_pass_id) 
    REFERENCES log_pass(log_pass_id),
  -- Unique columns in this table
  -- Nation
  nati                         TEXT,
  -- Range
  rang                         TEXT,
  -- Township
  town                         TEXT,
  -- Section
  sect                         TEXT,
  -- Latitude and Longitude in radians.
  lati                          DOUBLE PRECISION,
  long                          DOUBLE PRECISION,
  -- Field location
  fl                            TEXT,
  -- State
  stat                          TEXT,
  -- County
  coun                          TEXT,
  -- Field name
  fn                            TEXT,
  -- Well name
  wn                            TEXT,
  -- Company name
  cn                            TEXT,
  date                          DATE,
  -- Top log interval
  tli                           DOUBLE PRECISION,
  -- Top log interval
  bli                           DOUBLE PRECISION,
  -- Depth driller
  tdd                           DOUBLE PRECISION,
  -- Depth logger
  tdl                           DOUBLE PRECISION,
  -- Units of tli, bli, tdd, tdl in LIS style
  unit                          VARCHAR(4),
  -- API well number.
  -- See: https://en.wikipedia.org/wiki/API_well_number which says 14 digits.
  -- 12 digits is also common.
  apin                          VARCHAR(14),
  -- Logging unit location and engineer.
  -- perhaps useful for identifying the location.
  lul                           TEXT,
  engi                          TEXT,
  -- Header identifier, useful for describing the log pass.
  hide                          TEXT,
);
```



