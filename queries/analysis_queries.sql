-- ============================================================
-- HEALTH DATABASE - ANALYSIS QUERIES
-- Database: imdb, Schema: public
-- ============================================================

-- ============================================================
-- QUERY 1: Monthly Revenue and Patient Volume
-- ============================================================
SELECT 
    d.year,
    d.month_name,
    COUNT(f.visit_id) AS total_patients,
    ROUND(SUM(f.billing_amount)::numeric, 2) AS total_revenue,
    ROUND(AVG(f.billing_amount)::numeric, 2) AS avg_billing,
    ROUND(AVG(f.length_of_stay)::numeric, 1) AS avg_stay_days
FROM public.fact_patient_visits f
JOIN public."date" d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- ============================================================
-- QUERY 2: Top Medical Conditions by Cost and Volume
-- ============================================================
SELECT 
    c.condition_name,
    COUNT(f.visit_id) AS patient_count,
    ROUND(SUM(f.billing_amount)::numeric, 2) AS total_cost,
    ROUND(AVG(f.billing_amount)::numeric, 2) AS avg_cost_per_patient,
    ROUND(AVG(f.length_of_stay)::numeric, 1) AS avg_stay_days
FROM public.fact_patient_visits f
JOIN public.medical_condition c ON f.condition_key = c.condition_key
GROUP BY c.condition_name
ORDER BY total_cost DESC;

-- ============================================================
-- QUERY 3: Insurance Provider Analysis
-- ============================================================
SELECT 
    i.insurance_provider,
    COUNT(*) AS patients,
    ROUND(AVG(f.billing_amount)::numeric, 2) AS avg_bill,
    ROUND(SUM(f.billing_amount)::numeric, 2) AS total_bill
FROM public.fact_patient_visits f
JOIN public.insurance i ON f.insurance_key = i.insurance_key
GROUP BY i.insurance_provider
ORDER BY total_bill DESC;

-- ============================================================
-- QUERY 4: Doctor Workload Analysis
-- ============================================================
SELECT 
    d.doctor_name,
    d.specialty,
    COUNT(f.visit_id) AS patients_handled,
    ROUND(SUM(f.billing_amount)::numeric, 2) AS total_revenue,
    ROUND(AVG(f.billing_amount)::numeric, 2) AS avg_billing
FROM public.fact_patient_visits f
JOIN public.doctor d ON f.doctor_key = d.doctor_key
GROUP BY d.doctor_name, d.specialty
ORDER BY patients_handled DESC
LIMIT 10;

-- ============================================================
-- QUERY 5: Admission Type Efficiency
-- ============================================================
SELECT 
    a.admission_type,
    COUNT(*) AS visits,
    ROUND(AVG(f.length_of_stay)::numeric, 1) AS avg_stay,
    ROUND(AVG(f.billing_amount)::numeric, 2) AS avg_cost,
    ROUND(SUM(f.billing_amount)::numeric, 2) AS total_cost
FROM public.fact_patient_visits f
JOIN public.admission_type a ON f.admission_type_key = a.admission_key
GROUP BY a.admission_type
ORDER BY avg_cost DESC;