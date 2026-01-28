#!/bin/bash
# Email System Status Checker
# This script helps diagnose email scheduling and delivery issues

echo "========================================"
echo "  VOCA RECALLER EMAIL SYSTEM STATUS"
echo "========================================"
echo ""

# Check current time
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. CURRENT TIME & TIMEZONE INFO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Taipei Time: $(TZ='Asia/Taipei' date '+%Y-%m-%d %H:%M:%S %Z')"
echo "   UTC Time:    $(TZ='UTC' date '+%Y-%m-%d %H:%M:%S %Z')"
echo "   Server Time: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

# Check Docker containers
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. DOCKER CONTAINERS STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker ps --filter "name=voca_recaller" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Check email service configuration - FULL TABLE
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. EMAIL SERVICE TABLE (FULL DETAILS)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -e \
"SELECT 
    id,
    user_id,
    database_id,
    service_name,
    send_time,
    timezone,
    frequency,
    vocabulary_count,
    selection_method,
    is_active,
    DATE_FORMAT(last_sent_at, '%Y-%m-%d %H:%i:%s') as last_sent_at,
    DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at,
    DATE_FORMAT(updated_at, '%Y-%m-%d %H:%i:%s') as updated_at
FROM email_services 
ORDER BY id;" 2>/dev/null
echo ""

# Calculate expected UTC time for each service
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. EXPECTED UTC SCHEDULE (Calculated)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -e \
"SELECT 
    id,
    service_name,
    CONCAT(send_time, ' ', timezone) as 'Local Time',
    frequency,
    is_active,
    CASE 
        WHEN timezone = 'Asia/Taipei' THEN DATE_SUB(send_time, INTERVAL 8 HOUR)
        WHEN timezone = 'UTC' THEN send_time
        ELSE send_time
    END as 'Expected UTC Time'
FROM email_services 
WHERE is_active = 1
ORDER BY id;" 2>/dev/null
echo ""

# Check user and database relationship
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. USER & DATABASE INFO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -e \
"SELECT u.id, u.email, u.first_name, u.is_active as user_active,
        COUNT(DISTINCT nd.id) as databases_count,
        COUNT(DISTINCT es.id) as services_count
FROM users u
LEFT JOIN notion_databases nd ON u.id = nd.user_id
LEFT JOIN email_services es ON u.id = es.user_id
GROUP BY u.id;" 2>/dev/null
echo ""

# Check SMTP configuration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. SMTP CONFIGURATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec voca_recaller_backend printenv | grep SMTP | sed 's/\(SMTP_PASSWORD=\).*/\1***HIDDEN***/' || echo "   ⚠️  No SMTP variables found"
echo ""

# Check recent email logs with full details
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. EMAIL LOGS (Last 10 with full details)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -e \
"SELECT 
    id,
    user_id,
    DATE_FORMAT(sent_at, '%Y-%m-%d %H:%i:%s') as sent_at_utc,
    status,
    JSON_LENGTH(vocabulary_items) as vocab_count,
    error_message
FROM email_logs 
ORDER BY sent_at DESC 
LIMIT 10;" 2>/dev/null
echo ""

# Check Celery Beat logs - MORE DETAILS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. CELERY BEAT SCHEDULER LOGS (Last 50 lines)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Looking for: Schedule loads, cron schedules, and task dispatches..."
docker logs voca_recaller_celery_beat --tail 50 2>&1 | grep -v "DEBUG"
echo ""

# Check for scheduled tasks in Beat logs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9. CELERY BEAT - LOADED SCHEDULES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Searching for 'Scheduled:' entries..."
docker logs voca_recaller_celery_beat 2>&1 | grep -i "scheduled:" | tail -20
if [ $? -ne 0 ]; then
    echo "   ⚠️  No 'Scheduled:' entries found in Beat logs"
fi
echo ""

echo "   Searching for 'Loaded.*schedules' entries..."
docker logs voca_recaller_celery_beat 2>&1 | grep -i "loaded.*schedule" | tail -10
if [ $? -ne 0 ]; then
    echo "   ⚠️  No 'Loaded schedules' entries found"
fi
echo ""

# Check Redis for pending tasks
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "10. REDIS STATUS & PENDING TASKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Redis Keys (Celery related):"
docker exec voca_recaller_redis redis-cli KEYS "*celery*" 2>/dev/null | head -20
echo ""
echo "   Celery Queue Length:"
docker exec voca_recaller_redis redis-cli LLEN celery 2>/dev/null || echo "   ⚠️  Cannot connect to Redis"
echo ""
echo "   Recent tasks in queue (if any):"
docker exec voca_recaller_redis redis-cli LRANGE celery 0 5 2>/dev/null
echo ""

# Check Celery Worker logs - COMPREHENSIVE
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "11. CELERY WORKER LOGS (Last 100 lines)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Full recent logs:"
docker logs voca_recaller_celery --tail 100 2>&1
echo ""

# Check for email-related task executions
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "12. CELERY WORKER - EMAIL TASK ACTIVITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Searching for 'send_email_service_task' executions..."
docker logs voca_recaller_celery 2>&1 | grep -i "send_email_service_task" | tail -20
if [ $? -ne 0 ]; then
    echo "   ⚠️  No email task executions found"
fi
echo ""

echo "   Searching for task received events..."
docker logs voca_recaller_celery 2>&1 | grep -i "received\|task" | tail -20
echo ""

# Check for errors in worker
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "13. CELERY WORKER - ERRORS & WARNINGS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker logs voca_recaller_celery 2>&1 | grep -i "error\|warning\|exception\|failed" | tail -20
if [ $? -ne 0 ]; then
    echo "   ✅ No errors found in worker logs"
fi
echo ""

# Check backend logs for email-related activity
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "14. BACKEND APPLICATION LOGS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Recent backend logs (last 30 lines):"
docker logs voca_recaller_backend --tail 30 2>&1 | grep -v "GET /api" | grep -v "OPTIONS"
echo ""

# Check if services are being reloaded
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "15. SCHEDULE RELOAD ACTIVITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Looking for reload_email_schedules task activity..."
docker logs voca_recaller_celery 2>&1 | grep -i "reload_email_schedules" | tail -10
if [ $? -ne 0 ]; then
    echo "   ⚠️  No reload task activity found"
fi
echo ""
docker logs voca_recaller_celery_beat 2>&1 | grep -i "reload" | tail -10
echo ""

# Summary and recommendations
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "16. DIAGNOSTIC SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count active services
ACTIVE_SERVICES=$(docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -se \
"SELECT COUNT(*) FROM email_services WHERE is_active=1;" 2>/dev/null)

# Count recent emails
RECENT_EMAILS=$(docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -se \
"SELECT COUNT(*) FROM email_logs WHERE sent_at > NOW() - INTERVAL 24 HOUR;" 2>/dev/null)

# Count failed emails
FAILED_EMAILS=$(docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -se \
"SELECT COUNT(*) FROM email_logs WHERE status='failed' AND sent_at > NOW() - INTERVAL 24 HOUR;" 2>/dev/null)

echo "   📊 Active Email Services: $ACTIVE_SERVICES"
echo "   📧 Emails Sent (Last 24h): $RECENT_EMAILS"
echo "   ❌ Failed Emails (Last 24h): $FAILED_EMAILS"
echo ""

# Recommendations
echo "   📋 TROUBLESHOOTING CHECKLIST:"
echo "   ☐ Verify email service is_active = 1 (Section 3)"
echo "   ☐ Check expected UTC time matches your intention (Section 4)"
echo "   ☐ Confirm SMTP credentials are set (Section 6)"
echo "   ☐ Look for 'Scheduled:' in Beat logs (Section 9)"
echo "   ☐ Check if worker received tasks (Section 12)"
echo "   ☐ Review any errors in worker logs (Section 13)"
echo "   ☐ Verify Redis is accepting tasks (Section 10)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DIAGNOSTIC COMPLETE - $(date '+%Y-%m-%d %H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
