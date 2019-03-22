# Test Sets

## Medium Size Test Set


The Medium Size Test Set is 20,000+ files (100Gb+) of typical oilfield data. Here is the approximate breakdown of the test set:

| File Type | Files | Total Size | Notes |
| --- | ---: | ---: | --- |
| LAS v1.2 | ~500 | ~1Gb | Largest file is around 16Mb |
| LAS v2.0 | ~20,000 | ~30Gb | Largest file is around 250Mb |
| LAS v3.0 | ~0 | ~0 | If present then not considered significant. |
| LIS | ~2000 | ~2GB | Largest file is around 60Mb. Around half have TIF markers. |
| DLIS (RP66V1) | ~800 | ~100GB | Largest file is around 4GB. About one quarter have TIF markers. |
| DLIS (RP66V2) | ~0 | ~0 | If present then not considered significant. |
| Other | Various | Various | Various files such as PDF, TIFF, miscellaneous binary files and unstructured ASCII. If present then not considered significant. |

The layout of the test set is typical of an oilfield repository, typically by well, with a well having an unspecified directory structure and a mix of file types in each directory.

Histograms of file sizes from 2^10 bytes (1kb) bytes to 2^32 bytes (4Gb):

LAS 2.0

```
>2**10 | 
>2**11 | 
>2**12 | 
>2**13 | +
>2**14 | ++
>2**15 | +++++++
>2**16 | +++++++++++
>2**17 | +++++++++
>2**18 | ++++++++++++++
>2**19 | ++++++++++++
>2**20 | ++++++++++++++++++++++++++++++++++++++++
>2**21 | +++++++++++++++++++++++
>2**22 | ++
>2**23 | +
>2**24 | 
>2**25 | 
>2**26 | 
>2**27 | 
>2**28 | 
>2**29 | 
>2**30 | 
>2**31 | 
>2**32 | 
```

LIS

```
>2**10 | 
>2**11 | +
>2**12 | +++++++
>2**13 | ++++++
>2**14 | ++++++++++++++++++++
>2**15 | +++++++++++++
>2**16 | +++++++++++++++++++
>2**17 | ++++++++++++++++++++++++++++++++++++++++
>2**18 | ++++++++++++++++++++++++++++
>2**19 | ++++++++++++++++++++++
>2**20 | ++++++++++++
>2**21 | +++++++++++++
>2**22 | ++++
>2**23 | +++
>2**24 | ++++
>2**25 | ++
>2**26 | 
>2**27 | 
>2**28 | 
>2**29 | 
>2**30 | 
>2**31 | 
>2**32 | 
```

RP66V1


```
>2**10 | 
>2**11 | 
>2**12 | 
>2**13 | 
>2**14 | 
>2**15 | 
>2**16 | +++
>2**17 | ++++++++++++++++++++++++++++++++++++++++
>2**18 | ++++++++++++++++++++++++++++
>2**19 | ++++++++++++++++++++++++++++++++
>2**20 | ++++++++++++++++++++
>2**21 | +++++++++++++++++++++++++++++
>2**22 | ++++++++++++++++++++++++++++++
>2**23 | ++++++++++++++++++++
>2**24 | ++++++++++++++++++++
>2**25 | +++++++++++++++++++
>2**26 | +++++++++++++++++++++
>2**27 | +++++++++++++++++
>2**28 | +++++++++
>2**29 | ++++++
>2**30 | +++++++++
>2**31 | +++++
>2**32 | 
```
