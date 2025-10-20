## Capacitance Requirements by Band

For each band, I'll calculate the required total capacitance range, then show what comes from where.

---

## Calculation Method

**Resonant frequency formula:**

```
f = 1 / (2π√(LC))

Solving for C:
C = 1 / (4π² × L × f²)
```

---

## Band-by-Band Breakdown

### 160m Band (1.8 - 2.0 MHz)

**Inductor: L1 = 500 nH (with 2nF permanent)**

|Frequency|Required Total C|From L1 Permanent|From C_160m Fixed|From Variable Bank|
|---|---|---|---|---|
|2.0 MHz (high)|12,665 pF|2,000 pF|10,000 pF|665 pF|
|1.8 MHz (low)|15,633 pF|2,000 pF|10,000 pF|3,633 pF|
|**Range needed**|**12.7 - 15.6 nF**|**2.0 nF**|**10.0 nF**|**665 - 3,633 pF**|

**Variable bank must provide: 665 to 3,633 pF (span of 2,968 pF)**

✓ C0-C8 bank range: 0 - 4,320 pF (covers required range)

---

### 80m Band (3.5 - 4.0 MHz)

**Inductor: L1 = 500 nH (with 2nF permanent)**

|Frequency|Required Total C|From L1 Permanent|From Fixed Cap|From Variable Bank|
|---|---|---|---|---|
|4.0 MHz (high)|3,166 pF|2,000 pF|0 pF|1,166 pF|
|3.5 MHz (low)|4,137 pF|2,000 pF|0 pF|2,137 pF|
|**Range needed**|**3.17 - 4.14 nF**|**2.0 nF**|**None**|**1,166 - 2,137 pF**|

**Variable bank must provide: 1,166 to 2,137 pF (span of 971 pF)**

✓ C0-C8 bank range: 0 - 4,320 pF (covers required range)

---

### 40m Band (7.0 - 7.3 MHz)

**Inductor: L2 = 180 nH (no permanent cap)**

|Frequency|Required Total C|From L2 Permanent|From Fixed Cap|From Variable Bank|
|---|---|---|---|---|
|7.3 MHz (high)|2,657 pF|0 pF|0 pF|2,657 pF|
|7.0 MHz (low)|2,898 pF|0 pF|0 pF|2,898 pF|
|**Range needed**|**2.66 - 2.90 nF**|**0 nF**|**None**|**2,657 - 2,898 pF**|

**Variable bank must provide: 2,657 to 2,898 pF (span of 241 pF)**

✓ C0-C8 bank range: 0 - 4,320 pF (covers required range)

---

### 30m Band (10.1 - 10.15 MHz)

**Inductor: L2 = 180 nH (no permanent cap)**

|Frequency|Required Total C|From L2 Permanent|From Fixed Cap|From Variable Bank|
|---|---|---|---|---|
|10.15 MHz (high)|1,372 pF|0 pF|0 pF|1,372 pF|
|10.1 MHz (low)|1,385 pF|0 pF|0 pF|1,385 pF|
|**Range needed**|**1.37 - 1.39 nF**|**0 nF**|**None**|**1,372 - 1,385 pF**|

**Variable bank must provide: 1,372 to 1,385 pF (span of 13 pF)**

✓ C0-C8 bank range: 0 - 4,320 pF (covers required range)

---

### 20m Band (14.0 - 14.35 MHz)

**Inductor: L2 = 180 nH (no permanent cap)**

|Frequency|Required Total C|From L2 Permanent|From Fixed Cap|From Variable Bank|
|---|---|---|---|---|
|14.35 MHz (high)|685 pF|0 pF|0 pF|685 pF|
|14.0 MHz (low)|720 pF|0 pF|0 pF|720 pF|
|**Range needed**|**685 - 720 pF**|**0 nF**|**None**|**685 - 720 pF**|

**Variable bank must provide: 685 to 720 pF (span of 35 pF)**

✓ C0-C7 bank range: 0 - 1,020 pF (covers required range)

---

### 17m Band (18.068 - 18.168 MHz)

**Inductor: L3 = 68 nH (no permanent cap)**

|Frequency|Required Total C|From L3 Permanent|From Fixed Cap|From Variable Bank|
|---|---|---|---|---|
|18.168 MHz (high)|1,128 pF|0 pF|0 pF|1,128 pF|
|18.068 MHz (low)|1,141 pF|0 pF|0 pF|1,141 pF|
|**Range needed**|**1.13 - 1.14 nF**|**0 nF**|**None**|**1,128 - 1,141 pF**|

**Variable bank must provide: 1,128 to 1,141 pF (span of 13 pF)**

✓ C0-C7 bank range: 0 - 1,020 pF **WAIT - DOESN'T COVER!** ✗

**Problem detected!**

---

### 15m Band (21.0 - 21.45 MHz)

**Inductor: L2 ‖ L3 = 49.4 nH (parallel inductors)**

|Frequency|Required Total C|From Permanent|From Fixed Cap|From Variable Bank|
|---|---|---|---|---|
|21.45 MHz (high)|1,117 pF|0 pF|0 pF|1,117 pF|
|21.0 MHz (low)|1,165 pF|0 pF|0 pF|1,165 pF|
|**Range needed**|**1.12 - 1.17 nF**|**0 nF**|**None**|**1,117 - 1,165 pF**|

**Variable bank must provide: 1,117 to 1,165 pF (span of 48 pF)**

✓ C0-C7 bank range: 0 - 1,020 pF **DOESN'T COVER!** ✗

---

### 12m Band (24.89 - 24.99 MHz)

**Inductor: L2 ‖ L3 = 49.4 nH (parallel inductors)**

|Frequency|Required Total C|From Permanent|From Fixed Cap|From Variable Bank|
|---|---|---|---|---|
|24.99 MHz (high)|826 pF|0 pF|0 pF|826 pF|
|24.89 MHz (low)|832 pF|0 pF|0 pF|832 pF|
|**Range needed**|**826 - 832 pF**|**0 nF**|**None**|**826 - 832 pF**|

**Variable bank must provide: 826 to 832 pF (span of 6 pF)**

✓ C0-C7 bank range: 0 - 1,020 pF (covers required range)

---

### 10m Band (28.0 - 29.7 MHz)

**Inductor: L2 ‖ L3 = 49.4 nH (parallel inductors)**

|Frequency|Required Total C|From Permanent|From Fixed Cap|From Variable Bank|
|---|---|---|---|---|
|29.7 MHz (high)|582 pF|0 pF|0 pF|582 pF|
|28.0 MHz (low)|652 pF|0 pF|0 pF|652 pF|
|**Range needed**|**582 - 652 pF**|**0 nF**|**None**|**582 - 652 pF**|

**Variable bank must provide: 582 to 652 pF (span of 70 pF)**

✓ C0-C7 bank range: 0 - 1,020 pF (covers required range)

---

## PROBLEM IDENTIFIED: 17m and 15m Don't Work! ✗

**17m and 15m need MORE than 1020 pF minimum capacitance!**

This is why **C8 = 3300 pF is actually needed** for these bands too.

Let me recalculate...

---

## Revised Analysis: Which Bands Need C8?

**Maximum capacitance from C0-C7 only: 1,020 pF**

**Bands requiring > 1020 pF:**

- 160m: 665 - 3,633 pF ✗ (needs C8)
- 80m: 1,166 - 2,137 pF ✗ (needs C8)
- 40m: 2,657 - 2,898 pF ✗ (needs C8)
- 30m: 1,372 - 1,385 pF ✗ (needs C8)
- 20m: 685 - 720 pF ✓ (C0-C7 sufficient)
- 17m: 1,128 - 1,141 pF ✗ (needs C8)
- 15m: 1,117 - 1,165 pF ✗ (needs C8)
- 12m: 826 - 832 pF ✓ (C0-C7 sufficient)
- 10m: 582 - 652 pF ✓ (C0-C7 sufficient)

**Only 20m, 12m, and 10m can work with C0-C7 alone!**

**All other bands need access to C8.**

---

## Summary Table: All Bands

|Band|Freq Range (MHz)|L Value|L Permanent C|Fixed C (switched)|Variable Bank Range Needed|Uses C8?|
|---|---|---|---|---|---|---|
|**160m**|1.8 - 2.0|500 nH|2.0 nF|10.0 nF|665 - 3,633 pF|**YES** ✓|
|**80m**|3.5 - 4.0|500 nH|2.0 nF|None|1,166 - 2,137 pF|**YES** ✓|
|**40m**|7.0 - 7.3|180 nH|0 nF|None|2,657 - 2,898 pF|**YES** ✓|
|**30m**|10.1 - 10.15|180 nH|0 nF|None|1,372 - 1,385 pF|**YES** ✓|
|**20m**|14.0 - 14.35|180 nH|0 nF|None|685 - 720 pF|No|
|**17m**|18.068 - 18.168|68 nH|0 nF|None|1,128 - 1,141 pF|**YES** ✓|
|**15m**|21.0 - 21.45|49.4 nH|0 nF|None|1,117 - 1,165 pF|**YES** ✓|
|**12m**|24.89 - 24.99|49.4 nH|0 nF|None|826 - 832 pF|No|
|**10m**|28.0 - 29.7|49.4 nH|0 nF|None|582 - 652 pF|No|

**C8 (3300 pF) is needed for 6 out of 9 bands!**

**The 9-bit capacitor bank (with C8 = 3300 pF) works for all bands.** ✓✓✓