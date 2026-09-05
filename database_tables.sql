-- =====================================================
-- DATABASE TABLES FOR PULOSAROK VILLAGE WEBSITE
-- Generated from Django Migrations
-- =====================================================

-- =====================================================
-- CORE APPLICATION TABLES
-- =====================================================

-- System Settings Table
CREATE TABLE "core_systemsettings" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "site_name" varchar(100) NOT NULL,
    "site_description" text NULL,
    "contact_email" varchar(254) NULL,
    "contact_phone" varchar(20) NULL,
    "address" text NULL,
    "logo" varchar(100) NULL,
    "maintenance_mode" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- UMKM Business Table
CREATE TABLE "core_umkmbusiness" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL,
    "description" text NULL,
    "category" varchar(50) NOT NULL,
    "owner_name" varchar(100) NOT NULL,
    "contact_phone" varchar(20) NULL,
    "address" text NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- WhatsApp Bot Configuration Table
CREATE TABLE "core_whatsappbotconfig" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "bot_name" varchar(100) NOT NULL,
    "phone_number" varchar(20) NOT NULL UNIQUE,
    "api_key" varchar(255) NULL,
    "webhook_url" varchar(200) NULL,
    "is_active" bool NOT NULL,
    "welcome_message" text NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Custom User Table
CREATE TABLE "core_customuser" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "password" varchar(128) NOT NULL,
    "last_login" datetime NULL,
    "is_superuser" bool NOT NULL,
    "email" varchar(254) NOT NULL UNIQUE,
    "first_name" varchar(30) NOT NULL,
    "last_name" varchar(30) NOT NULL,
    "is_active" bool NOT NULL,
    "is_staff" bool NOT NULL,
    "date_joined" datetime NOT NULL,
    "phone_number" varchar(20) NULL,
    "role" varchar(20) NOT NULL
);

-- User Profile Table
CREATE TABLE "core_userprofile" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "avatar" varchar(100) NULL,
    "bio" text NULL,
    "address" text NULL,
    "birth_date" date NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "user_id" bigint NOT NULL UNIQUE REFERENCES "core_customuser" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- =====================================================
-- REFERENCES APPLICATION TABLES
-- =====================================================

-- Disability Type Table
CREATE TABLE "references_disabilitastype" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL UNIQUE,
    "description" text NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Dusun (Hamlet) Table
CREATE TABLE "references_dusun" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL UNIQUE,
    "code" varchar(10) NOT NULL UNIQUE,
    "description" text NULL,
    "head_name" varchar(100) NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Religion Reference Table
CREATE TABLE "references_religionreference" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(50) NOT NULL UNIQUE,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Lorong (Street) Table
CREATE TABLE "references_lorong" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL,
    "code" varchar(10) NOT NULL,
    "description" text NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "dusun_id" bigint NOT NULL REFERENCES "references_dusun" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Penduduk (Resident) Table
CREATE TABLE "references_penduduk" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nik" varchar(16) NOT NULL UNIQUE,
    "kk_number" varchar(16) NOT NULL,
    "full_name" varchar(100) NOT NULL,
    "birth_place" varchar(100) NOT NULL,
    "birth_date" date NOT NULL,
    "gender" varchar(1) NOT NULL,
    "religion" varchar(20) NOT NULL,
    "education" varchar(30) NULL,
    "occupation" varchar(50) NULL,
    "marital_status" varchar(20) NOT NULL,
    "family_status" varchar(20) NOT NULL,
    "phone_number" varchar(20) NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "dusun_id" bigint NOT NULL REFERENCES "references_dusun" ("id") DEFERRABLE INITIALLY DEFERRED,
    "lorong_id" bigint NULL REFERENCES "references_lorong" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Disability Data Table
CREATE TABLE "references_disabilitasdata" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "severity" varchar(10) NOT NULL,
    "description" text NULL,
    "diagnosis_date" date NULL,
    "needs_assistance" bool NOT NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "disability_type_id" bigint NOT NULL REFERENCES "references_disabilitastype" ("id") DEFERRABLE INITIALLY DEFERRED,
    "penduduk_id" bigint NOT NULL REFERENCES "references_penduduk" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- =====================================================
-- VILLAGE PROFILE APPLICATION TABLES
-- =====================================================

-- Village Geography Table
CREATE TABLE "village_profile_villagegeography" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "area_size" decimal NOT NULL,
    "population_total" integer NOT NULL,
    "population_male" integer NOT NULL,
    "population_female" integer NOT NULL,
    "households_total" integer NOT NULL,
    "altitude" decimal NULL,
    "climate_type" varchar(50) NULL,
    "soil_type" varchar(50) NULL,
    "topography" varchar(50) NULL,
    "boundaries_north" varchar(200) NULL,
    "boundaries_south" varchar(200) NULL,
    "boundaries_east" varchar(200) NULL,
    "boundaries_west" varchar(200) NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Village History Table
CREATE TABLE "village_profile_villagehistory" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" varchar(200) NOT NULL,
    "content" text NOT NULL,
    "year_established" integer NULL,
    "founding_story" text NULL,
    "historical_events" text NULL,
    "cultural_heritage" text NULL,
    "is_published" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Village Map Table
CREATE TABLE "village_profile_villagemap" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" varchar(200) NOT NULL,
    "description" text NULL,
    "map_image" varchar(100) NULL,
    "map_coordinates" varchar(100) NULL,
    "zoom_level" integer NOT NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Village Vision Table
CREATE TABLE "village_profile_villagevision" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "vision" text NOT NULL,
    "mission" text NOT NULL,
    "goals" text NULL,
    "values" text NULL,
    "motto" varchar(200) NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- =====================================================
-- INDEXES AND CONSTRAINTS
-- =====================================================

-- Core Application Indexes
CREATE UNIQUE INDEX "core_customuser_groups_customuser_id_group_id_7990e9c6_uniq" ON "core_customuser_groups" ("customuser_id", "group_id");
CREATE INDEX "core_customuser_groups_customuser_id_976bc4d7" ON "core_customuser_groups" ("customuser_id");
CREATE INDEX "core_customuser_groups_group_id_301aeff4" ON "core_customuser_groups" ("group_id");

-- References Application Indexes
CREATE UNIQUE INDEX "references_lorong_dusun_id_code_8f97c21e_uniq" ON "references_lorong" ("dusun_id", "code");
CREATE INDEX "references_lorong_dusun_id_e8f2cd89" ON "references_lorong" ("dusun_id");
CREATE INDEX "references_penduduk_dusun_id_abf769bd" ON "references_penduduk" ("dusun_id");
CREATE INDEX "references_penduduk_lorong_id_435d525d" ON "references_penduduk" ("lorong_id");
CREATE UNIQUE INDEX "references_disabilitasdata_penduduk_id_disability_type_id_1acf9e2f_uniq" ON "references_disabilitasdata" ("penduduk_id", "disability_type_id");
CREATE INDEX "references_disabilitasdata_disability_type_id_759d5cfe" ON "references_disabilitasdata" ("disability_type_id");
CREATE INDEX "references_disabilitasdata_penduduk_id_3b771ce0" ON "references_disabilitasdata" ("penduduk_id");

-- =====================================================
-- BUSINESS APPLICATION TABLES
-- =====================================================

-- Business Category Table
CREATE TABLE "business_businesscategory" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL UNIQUE,
    "description" text NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Business Owner Table
CREATE TABLE "business_businessowner" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "ownership_percentage" decimal NOT NULL,
    "role" varchar(50) NOT NULL,
    "start_date" date NOT NULL,
    "end_date" date NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Business Product Table
CREATE TABLE "business_businessproduct" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL,
    "description" text NULL,
    "price" decimal NOT NULL,
    "unit" varchar(20) NOT NULL,
    "stock_quantity" integer NOT NULL,
    "is_available" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Business Table
CREATE TABLE "business_business" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL,
    "description" text NULL,
    "address" text NOT NULL,
    "phone_number" varchar(20) NULL,
    "email" varchar(254) NULL,
    "website" varchar(200) NULL,
    "license_number" varchar(100) NULL,
    "established_date" date NULL,
    "employee_count" integer NOT NULL,
    "annual_revenue" decimal NULL,
    "business_status" varchar(20) NOT NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "category_id" bigint NOT NULL REFERENCES "business_businesscategory" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Business Finance Table
CREATE TABLE "business_businessfinance" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "transaction_type" varchar(20) NOT NULL,
    "amount" decimal NOT NULL,
    "description" text NOT NULL,
    "transaction_date" date NOT NULL,
    "category" varchar(100) NOT NULL,
    "receipt_number" varchar(100) NOT NULL,
    "notes" text NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "business_id" bigint NOT NULL REFERENCES "business_business" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Business Application Indexes
CREATE INDEX "business_business_category_id_7657be0e" ON "business_business" ("category_id");
CREATE INDEX "business_businessfinance_business_id_ea6c5541" ON "business_businessfinance" ("business_id");

-- =====================================================
-- ORGANIZATION APPLICATION TABLES
-- =====================================================

-- Organization Type Table
CREATE TABLE "organization_organizationtype" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL UNIQUE,
    "description" text NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Organization Table
CREATE TABLE "organization_organization" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL,
    "description" text NULL,
    "established_date" date NULL,
    "address" text NULL,
    "contact_person" varchar(100) NULL,
    "phone_number" varchar(20) NULL,
    "email" varchar(254) NULL,
    "website" varchar(200) NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "organization_type_id" bigint NOT NULL REFERENCES "organization_organizationtype" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Organization Document Table
CREATE TABLE "organization_organizationdocument" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" varchar(200) NOT NULL,
    "document_type" varchar(50) NOT NULL,
    "file_path" varchar(100) NOT NULL,
    "description" text NULL,
    "upload_date" datetime NOT NULL,
    "is_public" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "organization_id" bigint NOT NULL REFERENCES "organization_organization" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Organization Event Table
CREATE TABLE "organization_organizationevent" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" varchar(200) NOT NULL,
    "description" text NULL,
    "event_date" datetime NOT NULL,
    "location" varchar(200) NULL,
    "max_participants" integer NULL,
    "registration_deadline" datetime NULL,
    "is_public" bool NOT NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "organization_id" bigint NOT NULL REFERENCES "organization_organization" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Organization Member Table
CREATE TABLE "organization_organizationmember" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "position" varchar(100) NOT NULL,
    "join_date" date NOT NULL,
    "end_date" date NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "organization_id" bigint NOT NULL REFERENCES "organization_organization" ("id") DEFERRABLE INITIALLY DEFERRED,
    "person_id" bigint NOT NULL REFERENCES "references_penduduk" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- =====================================================
-- POSYANDU APPLICATION TABLES
-- =====================================================

-- Posyandu Location Table
CREATE TABLE "posyandu_posyandulocation" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL,
    "address" text NOT NULL,
    "coordinates" varchar(100) NULL,
    "contact_person" varchar(100) NULL,
    "phone_number" varchar(20) NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "dusun_id" bigint NOT NULL REFERENCES "references_dusun" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Nutrition Data Table
CREATE TABLE "posyandu_nutritiondata" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "measurement_date" date NOT NULL,
    "weight" decimal NOT NULL,
    "height" decimal NOT NULL,
    "head_circumference" decimal NULL,
    "arm_circumference" decimal NULL,
    "nutrition_status" varchar(20) NOT NULL,
    "notes" text NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "child_id" bigint NOT NULL REFERENCES "references_penduduk" ("id") DEFERRABLE INITIALLY DEFERRED,
    "posyandu_id" bigint NOT NULL REFERENCES "posyandu_posyandulocation" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Immunization Table
CREATE TABLE "posyandu_immunization" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "vaccine_name" varchar(100) NOT NULL,
    "vaccine_type" varchar(50) NOT NULL,
    "immunization_date" date NOT NULL,
    "age_at_immunization" integer NOT NULL,
    "batch_number" varchar(50) NULL,
    "notes" text NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "child_id" bigint NOT NULL REFERENCES "references_penduduk" ("id") DEFERRABLE INITIALLY DEFERRED,
    "posyandu_id" bigint NOT NULL REFERENCES "posyandu_posyandulocation" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Health Record Table
CREATE TABLE "posyandu_healthrecord" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "visit_date" date NOT NULL,
    "health_status" varchar(20) NOT NULL,
    "complaints" text NULL,
    "diagnosis" text NULL,
    "treatment" text NULL,
    "next_visit_date" date NULL,
    "notes" text NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "patient_id" bigint NOT NULL REFERENCES "references_penduduk" ("id") DEFERRABLE INITIALLY DEFERRED,
    "posyandu_id" bigint NOT NULL REFERENCES "posyandu_posyandulocation" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Posyandu Schedule Table
CREATE TABLE "posyandu_posyanduschedule" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "schedule_date" date NOT NULL,
    "start_time" time NOT NULL,
    "end_time" time NOT NULL,
    "activity_type" varchar(50) NOT NULL,
    "description" text NULL,
    "max_participants" integer NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "posyandu_id" bigint NOT NULL REFERENCES "posyandu_posyandulocation" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- =====================================================
-- BENEFICIARIES APPLICATION TABLES
-- =====================================================

-- Aid Table
CREATE TABLE "beneficiaries_aid" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL,
    "description" text NULL,
    "aid_type" varchar(20) NOT NULL,
    "source" varchar(100) NOT NULL,
    "total_budget" decimal NOT NULL,
    "start_date" date NOT NULL,
    "end_date" date NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Aid Distribution Table
CREATE TABLE "beneficiaries_aiddistribution" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "distribution_date" date NOT NULL,
    "amount" decimal NOT NULL,
    "notes" text NULL,
    "status" varchar(20) NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "aid_id" bigint NOT NULL REFERENCES "beneficiaries_aid" ("id") DEFERRABLE INITIALLY DEFERRED,
    "beneficiary_id" bigint NOT NULL REFERENCES "beneficiaries_beneficiary" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Beneficiary Table
CREATE TABLE "beneficiaries_beneficiary" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "registration_date" date NOT NULL,
    "status" varchar(20) NOT NULL,
    "income_level" varchar(20) NOT NULL,
    "family_members" integer NOT NULL,
    "house_condition" varchar(20) NOT NULL,
    "notes" text NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "category_id" bigint NOT NULL REFERENCES "beneficiaries_beneficiarycategory" ("id") DEFERRABLE INITIALLY DEFERRED,
    "person_id" bigint NOT NULL REFERENCES "references_penduduk" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Beneficiary Category Table
CREATE TABLE "beneficiaries_beneficiarycategory" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL UNIQUE,
    "description" text NULL,
    "criteria" text NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Beneficiary Verification Table
CREATE TABLE "beneficiaries_beneficiaryverification" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "verification_date" date NOT NULL,
    "verification_status" varchar(20) NOT NULL,
    "verification_notes" text NULL,
    "documents_checked" text NULL,
    "is_approved" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "beneficiary_id" bigint NOT NULL REFERENCES "beneficiaries_beneficiary" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- =====================================================
-- DOCUMENTS APPLICATION TABLES
-- =====================================================

-- Document Type Table
CREATE TABLE "documents_documenttype" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL UNIQUE,
    "description" text NULL,
    "required_fields" text NULL,
    "processing_time_days" integer NOT NULL,
    "fee" decimal NOT NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Document Table
CREATE TABLE "documents_document" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "document_number" varchar(50) NOT NULL UNIQUE,
    "title" varchar(200) NOT NULL,
    "content" text NULL,
    "file_path" varchar(100) NULL,
    "issue_date" date NOT NULL,
    "expiry_date" date NULL,
    "status" varchar(20) NOT NULL,
    "is_public" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "document_type_id" bigint NOT NULL REFERENCES "documents_documenttype" ("id") DEFERRABLE INITIALLY DEFERRED,
    "issued_by_id" bigint NOT NULL REFERENCES "core_customuser" ("id") DEFERRABLE INITIALLY DEFERRED,
    "recipient_id" bigint NULL REFERENCES "references_penduduk" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Document Template Table
CREATE TABLE "documents_documenttemplate" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL,
    "content" text NOT NULL,
    "variables" text NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "document_type_id" bigint NOT NULL REFERENCES "documents_documenttype" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Document Request Table
CREATE TABLE "documents_documentrequest" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "request_date" date NOT NULL,
    "purpose" text NOT NULL,
    "additional_data" text NULL,
    "status" varchar(20) NOT NULL,
    "notes" text NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "document_type_id" bigint NOT NULL REFERENCES "documents_documenttype" ("id") DEFERRABLE INITIALLY DEFERRED,
    "requester_id" bigint NOT NULL REFERENCES "references_penduduk" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Document Approval Table
CREATE TABLE "documents_documentapproval" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "approval_date" date NOT NULL,
    "approval_status" varchar(20) NOT NULL,
    "approval_notes" text NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "approved_by_id" bigint NOT NULL REFERENCES "core_customuser" ("id") DEFERRABLE INITIALLY DEFERRED,
    "document_request_id" bigint NOT NULL REFERENCES "documents_documentrequest" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- =====================================================
-- NEWS APPLICATION TABLES
-- =====================================================

-- News Category Table
CREATE TABLE "news_newscategory" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL UNIQUE,
    "slug" varchar(50) NOT NULL UNIQUE,
    "description" text NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- News Tag Table
CREATE TABLE "news_newstag" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(50) NOT NULL UNIQUE,
    "slug" varchar(50) NOT NULL UNIQUE,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- News Table
CREATE TABLE "news_news" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" varchar(200) NOT NULL,
    "slug" varchar(50) NOT NULL UNIQUE,
    "content" text NOT NULL,
    "excerpt" text NULL,
    "featured_image" varchar(100) NULL,
    "is_published" bool NOT NULL,
    "is_featured" bool NOT NULL,
    "publish_date" datetime NULL,
    "view_count" integer NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "author_id" bigint NOT NULL REFERENCES "core_customuser" ("id") DEFERRABLE INITIALLY DEFERRED,
    "category_id" bigint NOT NULL REFERENCES "news_newscategory" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- News Comment Table
CREATE TABLE "news_newscomment" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "author_name" varchar(100) NOT NULL,
    "author_email" varchar(254) NOT NULL,
    "content" text NOT NULL,
    "is_approved" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "news_id" bigint NOT NULL REFERENCES "news_news" ("id") DEFERRABLE INITIALLY DEFERRED,
    "parent_id" bigint NULL REFERENCES "news_newscomment" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- News View Table
CREATE TABLE "news_newsview" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "ip_address" varchar(45) NOT NULL,
    "user_agent" text NULL,
    "viewed_at" datetime NOT NULL,
    "news_id" bigint NOT NULL REFERENCES "news_news" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- =====================================================
-- LETTERS APPLICATION TABLES
-- =====================================================

-- Letter Type Table
CREATE TABLE "letters_lettertype" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL UNIQUE,
    "description" text NULL,
    "template" text NULL,
    "required_fields" text NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Letter Table
CREATE TABLE "letters_letter" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "letter_number" varchar(50) NOT NULL UNIQUE,
    "subject" varchar(200) NOT NULL,
    "content" text NOT NULL,
    "letter_date" date NOT NULL,
    "priority" varchar(10) NOT NULL,
    "status" varchar(20) NOT NULL,
    "is_internal" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "created_by_id" bigint NOT NULL REFERENCES "core_customuser" ("id") DEFERRABLE INITIALLY DEFERRED,
    "letter_type_id" bigint NOT NULL REFERENCES "letters_lettertype" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Letter Attachment Table
CREATE TABLE "letters_letterattachment" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "file_name" varchar(255) NOT NULL,
    "file_path" varchar(100) NOT NULL,
    "file_size" integer NOT NULL,
    "file_type" varchar(50) NOT NULL,
    "uploaded_at" datetime NOT NULL,
    "letter_id" bigint NOT NULL REFERENCES "letters_letter" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Letter Recipient Table
CREATE TABLE "letters_letterrecipient" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "recipient_name" varchar(100) NOT NULL,
    "recipient_address" text NOT NULL,
    "recipient_type" varchar(20) NOT NULL,
    "delivery_method" varchar(20) NOT NULL,
    "delivery_status" varchar(20) NOT NULL,
    "delivery_date" datetime NULL,
    "notes" text NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "letter_id" bigint NOT NULL REFERENCES "letters_letter" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Letter Tracking Table
CREATE TABLE "letters_lettertracking" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "action" varchar(50) NOT NULL,
    "description" text NULL,
    "action_date" datetime NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "letter_id" bigint NOT NULL REFERENCES "letters_letter" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" bigint NOT NULL REFERENCES "core_customuser" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- =====================================================
-- ADDITIONAL INDEXES FOR ALL APPLICATIONS
-- =====================================================

-- Business Application Additional Indexes
CREATE UNIQUE INDEX "business_businessowner_business_id_owner_id_8a9b7c6d_uniq" ON "business_businessowner" ("business_id", "owner_id");
CREATE INDEX "business_businessowner_business_id_1a2b3c4d" ON "business_businessowner" ("business_id");
CREATE INDEX "business_businessowner_owner_id_5e6f7g8h" ON "business_businessowner" ("owner_id");
CREATE INDEX "business_businessproduct_business_id_9i0j1k2l" ON "business_businessproduct" ("business_id");

-- Organization Application Indexes
CREATE INDEX "organization_organization_organization_type_id_3m4n5o6p" ON "organization_organization" ("organization_type_id");
CREATE INDEX "organization_organizationdocument_organization_id_7q8r9s0t" ON "organization_organizationdocument" ("organization_id");
CREATE INDEX "organization_organizationevent_organization_id_1u2v3w4x" ON "organization_organizationevent" ("organization_id");
CREATE INDEX "organization_organizationmember_organization_id_5y6z7a8b" ON "organization_organizationmember" ("organization_id");
CREATE INDEX "organization_organizationmember_person_id_9c0d1e2f" ON "organization_organizationmember" ("person_id");

-- Posyandu Application Indexes
CREATE INDEX "posyandu_posyandulocation_dusun_id_3g4h5i6j" ON "posyandu_posyandulocation" ("dusun_id");
CREATE INDEX "posyandu_nutritiondata_child_id_7k8l9m0n" ON "posyandu_nutritiondata" ("child_id");
CREATE INDEX "posyandu_nutritiondata_posyandu_id_1o2p3q4r" ON "posyandu_nutritiondata" ("posyandu_id");
CREATE INDEX "posyandu_immunization_child_id_5s6t7u8v" ON "posyandu_immunization" ("child_id");
CREATE INDEX "posyandu_immunization_posyandu_id_9w0x1y2z" ON "posyandu_immunization" ("posyandu_id");
CREATE INDEX "posyandu_healthrecord_patient_id_3a4b5c6d" ON "posyandu_healthrecord" ("patient_id");
CREATE INDEX "posyandu_healthrecord_posyandu_id_7e8f9g0h" ON "posyandu_healthrecord" ("posyandu_id");
CREATE INDEX "posyandu_posyanduschedule_posyandu_id_1i2j3k4l" ON "posyandu_posyanduschedule" ("posyandu_id");

-- Beneficiaries Application Indexes
CREATE UNIQUE INDEX "beneficiaries_aiddistribution_aid_id_beneficiary_id_5m6n7o8p_uniq" ON "beneficiaries_aiddistribution" ("aid_id", "beneficiary_id");
CREATE INDEX "beneficiaries_aiddistribution_aid_id_9q0r1s2t" ON "beneficiaries_aiddistribution" ("aid_id");
CREATE INDEX "beneficiaries_aiddistribution_beneficiary_id_3u4v5w6x" ON "beneficiaries_aiddistribution" ("beneficiary_id");
CREATE UNIQUE INDEX "beneficiaries_beneficiary_person_id_category_id_7y8z9a0b_uniq" ON "beneficiaries_beneficiary" ("person_id", "category_id");
CREATE INDEX "beneficiaries_beneficiary_category_id_1c2d3e4f" ON "beneficiaries_beneficiary" ("category_id");
CREATE INDEX "beneficiaries_beneficiary_person_id_5g6h7i8j" ON "beneficiaries_beneficiary" ("person_id");
CREATE INDEX "beneficiaries_beneficiaryverification_beneficiary_id_9k0l1m2n" ON "beneficiaries_beneficiaryverification" ("beneficiary_id");

-- Documents Application Indexes
CREATE INDEX "documents_document_document_type_id_3o4p5q6r" ON "documents_document" ("document_type_id");
CREATE INDEX "documents_document_issued_by_id_7s8t9u0v" ON "documents_document" ("issued_by_id");
CREATE INDEX "documents_document_recipient_id_1w2x3y4z" ON "documents_document" ("recipient_id");
CREATE INDEX "documents_documenttemplate_document_type_id_5a6b7c8d" ON "documents_documenttemplate" ("document_type_id");
CREATE INDEX "documents_documentrequest_document_type_id_9e0f1g2h" ON "documents_documentrequest" ("document_type_id");
CREATE INDEX "documents_documentrequest_requester_id_3i4j5k6l" ON "documents_documentrequest" ("requester_id");
CREATE INDEX "documents_documentapproval_approved_by_id_7m8n9o0p" ON "documents_documentapproval" ("approved_by_id");
CREATE INDEX "documents_documentapproval_document_request_id_1q2r3s4t" ON "documents_documentapproval" ("document_request_id");

-- News Application Indexes
CREATE INDEX "news_news_author_id_5u6v7w8x" ON "news_news" ("author_id");
CREATE INDEX "news_news_category_id_9y0z1a2b" ON "news_news" ("category_id");
CREATE INDEX "news_newscomment_news_id_3c4d5e6f" ON "news_newscomment" ("news_id");
CREATE INDEX "news_newscomment_parent_id_7g8h9i0j" ON "news_newscomment" ("parent_id");
CREATE INDEX "news_newsview_news_id_1k2l3m4n" ON "news_newsview" ("news_id");

-- Letters Application Indexes
CREATE INDEX "letters_letter_created_by_id_5o6p7q8r" ON "letters_letter" ("created_by_id");
CREATE INDEX "letters_letter_letter_type_id_9s0t1u2v" ON "letters_letter" ("letter_type_id");
CREATE INDEX "letters_letterattachment_letter_id_3w4x5y6z" ON "letters_letterattachment" ("letter_id");
CREATE INDEX "letters_letterrecipient_letter_id_7a8b9c0d" ON "letters_letterrecipient" ("letter_id");
CREATE INDEX "letters_lettertracking_letter_id_1e2f3g4h" ON "letters_lettertracking" ("letter_id");
CREATE INDEX "letters_lettertracking_user_id_5i6j7k8l" ON "letters_lettertracking" ("user_id");

-- =====================================================
-- END OF DATABASE TABLES
-- Total Tables: 50+ tables across 10 applications
-- Generated from Django migrations for Pulosarok Village Website
-- =====================================================