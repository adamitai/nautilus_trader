# Monitoring Module Outputs

output "dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = "https://${data.aws_region.current.name}.console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "alarm_names" {
  description = "Names of the CloudWatch alarms"
  value = [
    aws_cloudwatch_metric_alarm.ecs_high_cpu.alarm_name,
    aws_cloudwatch_metric_alarm.ecs_high_memory.alarm_name,
    aws_cloudwatch_metric_alarm.rds_high_cpu.alarm_name,
    aws_cloudwatch_metric_alarm.rds_low_free_storage.alarm_name,
    aws_cloudwatch_metric_alarm.alb_high_response_time.alarm_name,
    aws_cloudwatch_metric_alarm.alb_high_5xx_errors.alarm_name,
    aws_cloudwatch_metric_alarm.trading_errors.alarm_name,
    aws_cloudwatch_metric_alarm.arbitrage_opportunities.alarm_name
  ]
}
