-- SQL examples for the analytics pipeline

-- 1) Latest KPI snapshot per entity
WITH latest AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY Symbol ORDER BY Date DESC) AS rn
    FROM stock_metrics
)
SELECT Symbol, Date AS latest_date,
       ROUND(Close, 2) AS close_price,
       ROUND(Daily_Return, 4) AS daily_return,
       ROUND(Volatility_20, 4) AS volatility_20,
       ROUND(Risk_Score, 1) AS risk_score,
       Trend_Signal, Long_Term_Trend
FROM latest
WHERE rn = 1
ORDER BY risk_score DESC;

-- 2) Explainable event counts by symbol
SELECT Symbol,
       COUNT(*) AS rows_processed,
       SUM(CASE WHEN Return_Anomaly = 1 THEN 1 ELSE 0 END) AS return_anomalies,
       SUM(CASE WHEN Volatility_Spike = 1 THEN 1 ELSE 0 END) AS volatility_spikes,
       SUM(CASE WHEN High_Volume_Event = 1 THEN 1 ELSE 0 END) AS high_volume_events,
       ROUND(AVG(Risk_Score), 1) AS avg_risk_score
FROM stock_metrics
GROUP BY Symbol
ORDER BY volatility_spikes DESC, avg_risk_score DESC;

-- 3) Simulated device-telemetry reuse example
SELECT Service, Software_Version,
       COUNT(*) AS rows_analyzed,
       ROUND(AVG(Signal_Latency_ms), 2) AS avg_latency_ms,
       ROUND(AVG(Packet_Loss_Rate), 4) AS avg_packet_loss,
       SUM(Reconnect_Count) AS reconnect_count,
       SUM(CASE WHEN Telemetry_Anomaly = 1 THEN 1 ELSE 0 END) AS anomalies
FROM telemetry_metrics_simulated
GROUP BY Service, Software_Version
ORDER BY anomalies DESC, avg_latency_ms DESC;

-- 4) Batch pipeline monitoring
SELECT Batch_Number, Rows_Processed, Start_Date, End_Date,
       Return_Anomalies, Volatility_Spikes, High_Volume_Events, Max_Risk_Score
FROM pipeline_batch_log
ORDER BY Batch_Number;
