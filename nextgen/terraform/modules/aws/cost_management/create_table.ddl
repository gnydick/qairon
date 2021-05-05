CREATE EXTERNAL TABLE IF NOT EXISTS cost_and_usage	 (
identity_LineItemId String,
identity_TimeInterval String,
bill_InvoiceId String,
bill_BillingEntity String,
bill_BillType String,
bill_PayerAccountId String,
bill_BillingPeriodStartDate String,
bill_BillingPeriodEndDate String,
lineItem_UsageAccountId String,
lineItem_LineItemType String,
lineItem_UsageStartDate String,
lineItem_UsageEndDate String,
lineItem_ProductCode String,
lineItem_UsageType String,
lineItem_Operation String,
lineItem_AvailabilityZone String,
lineItem_ResourceId String,
lineItem_UsageAmount String,
lineItem_NormalizationFactor String,
lineItem_NormalizedUsageAmount String,
lineItem_CurrencyCode String,
lineItem_UnblendedRate String,
lineItem_UnblendedCost String,
lineItem_BlendedRate String,
lineItem_BlendedCost String,
lineItem_LineItemDescription String,
lineItem_TaxType String,
product_ProductName String,
product_accountAssistance String,
product_architecturalReview String,
product_architectureSupport String,
product_availability String,
product_bestPractices String,
product_cacheEngine String,
product_caseSeverityresponseTimes String,
product_clockSpeed String,
product_currentGeneration String,
product_customerServiceAndCommunities String,
product_databaseEdition String,
product_databaseEngine String,
product_dedicatedEbsThroughput String,
product_deploymentOption String,
product_description String,
product_durability String,
product_ebsOptimized String,
product_ecu String,
product_endpointType String,
product_engineCode String,
product_enhancedNetworkingSupported String,
product_executionFrequency String,
product_executionLocation String,
product_feeCode String,
product_feeDescription String,
product_freeQueryTypes String,
product_freeTrial String,
product_frequencyMode String,
product_fromLocation String,
product_fromLocationType String,
product_group String,
product_groupDescription String,
product_includedServices String,
product_instanceFamily String,
product_instanceType String,
product_io String,
product_launchSupport String,
product_licenseModel String,
product_location String,
product_locationType String,
product_maxIopsBurstPerformance String,
product_maxIopsvolume String,
product_maxThroughputvolume String,
product_maxVolumeSize String,
product_maximumStorageVolume String,
product_memory String,
product_messageDeliveryFrequency String,
product_messageDeliveryOrder String,
product_minVolumeSize String,
product_minimumStorageVolume String,
product_networkPerformance String,
product_operatingSystem String,
product_operation String,
product_operationsSupport String,
product_physicalProcessor String,
product_preInstalledSw String,
product_proactiveGuidance String,
product_processorArchitecture String,
product_processorFeatures String,
product_productFamily String,
product_programmaticCaseManagement String,
product_provisioned String,
product_queueType String,
product_requestDescription String,
product_requestType String,
product_routingTarget String,
product_routingType String,
product_servicecode String,
product_sku String,
product_softwareType String,
product_storage String,
product_storageClass String,
product_storageMedia String,
product_technicalSupport String,
product_tenancy String,
product_thirdpartySoftwareSupport String,
product_toLocation String,
product_toLocationType String,
product_training String,
product_transferType String,
product_usageFamily String,
product_usagetype String,
product_vcpu String,
product_version String,
product_volumeType String,
product_whoCanOpenCases String,
pricing_LeaseContractLength String,
pricing_OfferingClass String,
pricing_PurchaseOption String,
pricing_publicOnDemandCost String,
pricing_publicOnDemandRate String,
pricing_term String,
pricing_unit String,
reservation_AvailabilityZone String,
reservation_NormalizedUnitsPerReservation String,
reservation_NumberOfReservations String,
reservation_ReservationARN String,
reservation_TotalReservedNormalizedUnits String,
reservation_TotalReservedUnits String,
reservation_UnitsPerReservation String,
resourceTags_userName String,
resourceTags_usercostcategory String


)
    ROW FORMAT DELIMITED
      FIELDS TERMINATED BY ','
      ESCAPED BY '\\'
      LINES TERMINATED BY '\n'

STORED AS TEXTFILE
    LOCATION 's3://${bucket}/cost';