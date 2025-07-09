"""
Management command to clean up expired OTP codes.
Following Django best practices for periodic cleanup tasks.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from wagtailDemo.users.models import OTPCode


class Command(BaseCommand):
    help = 'Clean up expired OTP codes from the database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Remove OTP codes older than this many days (default: 7)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
    
    def handle(self, *args, **options):
        days_old = options['days']
        dry_run = options['dry_run']
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        # Find expired OTP codes
        expired_otps = OTPCode.objects.filter(
            created_at__lt=cutoff_date
        )
        
        count = expired_otps.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {count} OTP codes older than {days_old} days'
                )
            )
            
            if count > 0:
                self.stdout.write('Sample records that would be deleted:')
                for otp in expired_otps[:5]:  # Show first 5 records
                    self.stdout.write(f'  - {otp.phone_number}: {otp.created_at}')
                
                if count > 5:
                    self.stdout.write(f'  ... and {count - 5} more')
        else:
            # Actually delete the records
            expired_otps.delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {count} expired OTP codes'
                )
            )
        
        # Show remaining active OTP codes
        active_otps = OTPCode.objects.filter(
            is_used=False,
            expires_at__gt=timezone.now()
        ).count()
        
        self.stdout.write(f'Active OTP codes remaining: {active_otps}')
