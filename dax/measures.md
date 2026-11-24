-- ============================================================================
-- MEDIDAS DAX — SALES & BUSINESS PERFORMANCE (dw_demo1)
-- ============================================================================

-- 1. Métricas Base (Ventas, Costos, Utilidad, Descuentos, Volumen)
Gross Revenue =
SUMX ( FactSales, FactSales[Quantity] * FactSales[UnitPrice] )

Total Discount =
SUM ( FactSales[DiscountAmount] )

Total Revenue =
SUM ( FactSales[Revenue] )

Total Cost =
SUM ( FactSales[TotalCost] )

Total Gross Profit =
SUM ( FactSales[GrossProfit] )

Total Units =
SUM ( FactSales[Quantity] )

Total Orders =
DISTINCTCOUNT ( FactSales[SalesOrderID] )

Total Order Lines =
COUNTROWS ( FactSales )

Active Customers =
DISTINCTCOUNT ( FactSales[CustomerKey] )

-- 2. Rentabilidad, Descuentos y Promedios
Gross Margin % =
DIVIDE ( [Total Gross Profit], [Total Revenue], 0 )

Discount Rate % =
DIVIDE ( [Total Discount], [Gross Revenue], 0 )

Avg Order Value (AOV) =
DIVIDE ( [Total Revenue], [Total Orders], 0 )

Avg Units per Order =
DIVIDE ( [Total Units], [Total Orders], 0 )

Avg Revenue per Customer =
DIVIDE ( [Total Revenue], [Active Customers], 0 )

-- 3. Inteligencia de Tiempo (requiere DimDate marcada como Date Table en FullDate)
Revenue YTD =
TOTALYTD ( [Total Revenue], DimDate[FullDate] )

Gross Profit YTD =
TOTALYTD ( [Total Gross Profit], DimDate[FullDate] )

Revenue PY =
CALCULATE ( [Total Revenue], SAMEPERIODLASTYEAR ( DimDate[FullDate] ) )

Revenue YoY =
[Total Revenue] - [Revenue PY]

Revenue YoY % =
DIVIDE ( [Revenue YoY], [Revenue PY] )

Gross Margin % PY =
CALCULATE ( [Gross Margin %], SAMEPERIODLASTYEAR ( DimDate[FullDate] ) )

Gross Margin % YoY (bps) =
( [Gross Margin %] - [Gross Margin % PY] ) * 10000

-- 4. Concentración de Clientes (Pareto 80/20)
Customer Revenue Rank =
RANKX ( ALLSELECTED ( DimCustomer[CustomerName] ), [Total Revenue], , DESC, Dense )

Cumulative Customer Revenue =
VAR CurrentRev = [Total Revenue]
RETURN
CALCULATE (
    [Total Revenue],
    FILTER (
        ALLSELECTED ( DimCustomer[CustomerName] ),
        [Total Revenue] >= CurrentRev
    )
)

Cumulative Customer Revenue % =
DIVIDE (
    [Cumulative Customer Revenue],
    CALCULATE ( [Total Revenue], ALLSELECTED ( DimCustomer[CustomerName] ) ),
    0
)