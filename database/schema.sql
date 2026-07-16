-- ============================================================
-- HEALTH DATABASE STAR SCHEMA
-- Database: imdb
-- Schema: public
-- ============================================================

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS public.fact_patient_visits CASCADE;
DROP TABLE IF EXISTS public.district CASCADE;
DROP TABLE IF EXISTS public.test_results CASCADE;
DROP TABLE IF EXISTS public.admission_type CASCADE;
DROP TABLE IF EXISTS public.insurance CASCADE;
DROP TABLE IF EXISTS public.medication CASCADE;
DROP TABLE IF EXISTS public.medical_condition CASCADE;
DROP TABLE IF EXISTS public.doctor CASCADE;
DROP TABLE IF EXISTS public.hospital CASCADE;
DROP TABLE IF EXISTS public."date" CASCADE;
DROP TABLE IF EXISTS public.patient CASCADE;

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

-- 1. Patient Dimension
CREATE TABLE public.patient (
    patient_key SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) UNIQUE,
    full_name VARCHAR(100),
    gender VARCHAR(10),
    blood_type VARCHAR(5),
    age_group VARCHAR(20),
    age_range_start INT,
    age_range_end INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Date Dimension
CREATE TABLE public."date" (
    date_key INT PRIMARY KEY,
    full_date DATE,
    year INT,
    quarter INT,
    month INT,
    month_name VARCHAR(20),
    day INT,
    day_of_week INT,
    day_name VARCHAR(10),
    week_of_year INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Hospital Dimension
CREATE TABLE public.hospital (
    hospital_key SERIAL PRIMARY KEY,
    hospital_name VARCHAR(200),
    hospital_id VARCHAR(50),
    hospital_type VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Doctor Dimension
CREATE TABLE public.doctor (
    doctor_key SERIAL PRIMARY KEY,
    doctor_name VARCHAR(100),
    doctor_id VARCHAR(50),
    specialty VARCHAR(50),
    department VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Medical Condition Dimension
CREATE TABLE public.medical_condition (
    condition_key SERIAL PRIMARY KEY,
    condition_name VARCHAR(50),
    condition_category VARCHAR(50),
    severity_level VARCHAR(20),
    icd10_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Medication Dimension
CREATE TABLE public.medication (
    medication_key SERIAL PRIMARY KEY,
    medication_name VARCHAR(50),
    medication_category VARCHAR(50),
    drug_class VARCHAR(50),
    prescription_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Insurance Dimension
CREATE TABLE public.insurance (
    insurance_key SERIAL PRIMARY KEY,
    insurance_provider VARCHAR(100),
    insurance_type VARCHAR(50),
    coverage_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Admission Type Dimension
CREATE TABLE public.admission_type (
    admission_key SERIAL PRIMARY KEY,
    admission_type VARCHAR(20),
    description VARCHAR(100),
    priority_level INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Test Results Dimension
CREATE TABLE public.test_results (
    test_key SERIAL PRIMARY KEY,
    test_result VARCHAR(20),
    result_category VARCHAR(20),
    severity_indicator INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. District Dimension
CREATE TABLE public.district (
    district_key SERIAL PRIMARY KEY,
    district_name VARCHAR(100) NOT NULL,
    sub_region VARCHAR(100),
    region VARCHAR(50),
    estimated_population INT,
    is_urban BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- FACT TABLE
-- ============================================================

CREATE TABLE public.fact_patient_visits (
    visit_id SERIAL PRIMARY KEY,
    patient_key INT,
    date_key INT,
    hospital_key INT,
    doctor_key INT,
    condition_key INT,
    medication_key INT,
    insurance_key INT,
    admission_type_key INT,
    test_result_key INT,
    district_key INT,
    billing_amount DECIMAL(12,2),
    length_of_stay INT,
    room_number INT,
    age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- FOREIGN KEY CONSTRAINTS
-- ============================================================

ALTER TABLE public.fact_patient_visits
ADD CONSTRAINT fk_patient
FOREIGN KEY (patient_key) REFERENCES public.patient(patient_key);

ALTER TABLE public.fact_patient_visits
ADD CONSTRAINT fk_date
FOREIGN KEY (date_key) REFERENCES public."date"(date_key);

ALTER TABLE public.fact_patient_visits
ADD CONSTRAINT fk_hospital
FOREIGN KEY (hospital_key) REFERENCES public.hospital(hospital_key);

ALTER TABLE public.fact_patient_visits
ADD CONSTRAINT fk_doctor
FOREIGN KEY (doctor_key) REFERENCES public.doctor(doctor_key);

ALTER TABLE public.fact_patient_visits
ADD CONSTRAINT fk_condition
FOREIGN KEY (condition_key) REFERENCES public.medical_condition(condition_key);

ALTER TABLE public.fact_patient_visits
ADD CONSTRAINT fk_medication
FOREIGN KEY (medication_key) REFERENCES public.medication(medication_key);

ALTER TABLE public.fact_patient_visits
ADD CONSTRAINT fk_insurance
FOREIGN KEY (insurance_key) REFERENCES public.insurance(insurance_key);

ALTER TABLE public.fact_patient_visits
ADD CONSTRAINT fk_admission_type
FOREIGN KEY (admission_type_key) REFERENCES public.admission_type(admission_key);

ALTER TABLE public.fact_patient_visits
ADD CONSTRAINT fk_test_result
FOREIGN KEY (test_result_key) REFERENCES public.test_results(test_key);

ALTER TABLE public.fact_patient_visits
ADD CONSTRAINT fk_district
FOREIGN KEY (district_key) REFERENCES public.district(district_key);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX idx_fact_patient_key ON public.fact_patient_visits(patient_key);
CREATE INDEX idx_fact_date_key ON public.fact_patient_visits(date_key);
CREATE INDEX idx_fact_hospital_key ON public.fact_patient_visits(hospital_key);
CREATE INDEX idx_fact_doctor_key ON public.fact_patient_visits(doctor_key);
CREATE INDEX idx_fact_condition_key ON public.fact_patient_visits(condition_key);
CREATE INDEX idx_fact_medication_key ON public.fact_patient_visits(medication_key);
CREATE INDEX idx_fact_insurance_key ON public.fact_patient_visits(insurance_key);
CREATE INDEX idx_fact_admission_key ON public.fact_patient_visits(admission_type_key);
CREATE INDEX idx_fact_district_key ON public.fact_patient_visits(district_key);
CREATE INDEX idx_fact_billing_amount ON public.fact_patient_visits(billing_amount);

-- ============================================================
-- VERIFICATION: Check all tables have data
-- ============================================================

SELECT 'patient' AS table_name, COUNT(*) AS record_count FROM public.patient
UNION ALL
SELECT 'date', COUNT(*) FROM public."date"
UNION ALL
SELECT 'hospital', COUNT(*) FROM public.hospital
UNION ALL
SELECT 'doctor', COUNT(*) FROM public.doctor
UNION ALL
SELECT 'medical_condition', COUNT(*) FROM public.medical_condition
UNION ALL
SELECT 'medication', COUNT(*) FROM public.medication
UNION ALL
SELECT 'insurance', COUNT(*) FROM public.insurance
UNION ALL
SELECT 'admission_type', COUNT(*) FROM public.admission_type
UNION ALL
SELECT 'test_results', COUNT(*) FROM public.test_results
UNION ALL
SELECT 'district', COUNT(*) FROM public.district
UNION ALL
SELECT 'fact_patient_visits', COUNT(*) FROM public.fact_patient_visits
ORDER BY table_name;