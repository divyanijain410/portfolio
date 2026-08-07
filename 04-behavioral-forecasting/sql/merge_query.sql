SELECT s.Store, s.Dept, s.Date, s.Weekly_Sales, s.IsHoliday,
       f.Temperature, f.Fuel_Price, f.CPI, f.Unemployment,
       st.Type, st.Size
FROM sales s
JOIN features f ON s.Store = f.Store AND s.Date = f.Date
JOIN stores st ON s.Store = st.Store
