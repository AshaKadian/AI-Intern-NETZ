import numpy as np
import pandas as pd
list1 = [1,2,3,4]
array1=(np.array(list1))
print(array1)
list2=[[1,2,3],[4,5,6]]
array2=np.array(list2)
print(array2)
print(array2-2)

#series in pandas
array3=np.array([1,2,6,43])
series1=pd.Series(array3)
print(series1)

#dataframes in pandas
dataf=pd.DataFrame([
    ["asha",21],
    ["nisha",24]
],
                   columns=["name","age"])
print(dataf)
dataf.info()
dataf.value_counts()
dataf.nunique()