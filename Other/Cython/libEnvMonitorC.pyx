cpdef Pws(float T1):
    import math
    T = T1 + 273.5
        
    ### Method 1 - accurate but comp. intensive
    cdef float Tc = 647.096       # in K
    cdef float Pc = 220639.128   # in hPa-7.85951783
    cdef float C1 = -7.85951783
    cdef float C2 = 1.84408259
    cdef float C3 = -11.7866497
    cdef float C4 = 22.6807411
    cdef float C5 = -15.9618719
    cdef float C6 = 1.80122502
        
    cdef float nu = 1 - T/Tc
    cdef float Pws = Pc * math.exp((Tc/T)*(C1*nu + C2*pow(nu, 1.5) + C3*pow(nu, 3) + C4*pow(nu, 3.5) + C5*pow(nu, 4) + C6*pow(nu, 7.5)))    #  in hPa
    return Pws
        
cpdef absHumidity(float T1, float RH, float Pws):
    # https://www.hatchability.com/Vaisala.pdf
    cdef float T = T1 + 273.5
    cdef float C = 2.16679    # in gK/J
    cdef float RhA = C * (Pws * RH / 100) * 100/T
    return RhA
    
cpdef dewPointRH(float T1, float RH, float Pws):
    import math
    cdef float A = 1
    cdef float m = 1
    cdef float Tn = 0
    if T1 > -20 and T1 <= 50:
        A = 6.116441
        m = 7.591386
        Tn = 240.7263
    elif T1 > 50 and T1 <= 100:
        A = 6.004918
        m = 7.337936
        Tn = 229.3975
    
    cdef float Pw = Pws * RH / 100
    cdef float dew = Tn/((m/math.log10(Pw/A))-1)
    return dew
