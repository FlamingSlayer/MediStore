from decimal import Decimal

from django.core.management.base import BaseCommand

from api.models import Category, Product


class Command(BaseCommand):
    help = 'Seed default categories and products for local development.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--if-empty',
            action='store_true',
            help='Seed only when Product table is empty.',
        )

    def handle(self, *args, **options):
        if options['if_empty'] and Product.objects.exists():
            self.stdout.write(self.style.WARNING('Products already exist. Skipping seeding.'))
            return

        pain, _ = Category.objects.get_or_create(
            name='Pain Relief',
            defaults={'description': 'Pain relief medicines', 'icon': 'capsules'},
        )
        vit, _ = Category.objects.get_or_create(
            name='Vitamins',
            defaults={'description': 'Daily supplements', 'icon': 'capsules'},
        )
        rx, _ = Category.objects.get_or_create(
            name='Prescription',
            defaults={'description': 'Prescription drugs', 'icon': 'file-medical'},
        )

        samples = [
            (pain, 'Paracetamol 500', 'MediCare', 'For fever and pain', '500mg', Decimal('45.00'), Decimal('10.00'), False, 100),
            (pain, 'Ibuprofen 400', 'HealWell', 'Anti-inflammatory pain relief', '400mg', Decimal('65.00'), Decimal('5.00'), False, 80),
            (vit, 'Vitamin C', 'NutriPlus', 'Immunity support', '1000mg', Decimal('199.00'), Decimal('15.00'), False, 120),
            (vit, 'Multivitamin', 'NutriPlus', 'Daily vitamins', '1 tablet', Decimal('299.00'), Decimal('20.00'), False, 60),
            (rx, 'Amoxicillin', 'PharmaOne', 'Antibiotic', '500mg', Decimal('120.00'), Decimal('0.00'), True, 40),
            (rx, 'Metformin', 'GlucoCare', 'Diabetes management', '500mg', Decimal('160.00'), Decimal('8.00'), True, 50),
        ]

        created_count = 0
        for category, name, brand, description, dosage, price, discount, prescription_required, stock in samples:
            _, created = Product.objects.get_or_create(
                category=category,
                name=name,
                brand=brand,
                defaults={
                    'description': description,
                    'dosage': dosage,
                    'price': price,
                    'discount_percentage': discount,
                    'prescription_required': prescription_required,
                    'stock': stock,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Seed complete. New products created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total products: {Product.objects.count()}'))
