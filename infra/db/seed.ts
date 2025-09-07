import { PrismaClient, SpaceType } from '@prisma/client';

const prisma = new PrismaClient();

async function createSpaces(zoneId: number, start: number, end: number, type: SpaceType) {
  const data = Array.from({ length: end - start + 1 }).map((_, idx) => ({
    zoneId,
    number: start + idx,
    type,
  }));
  await prisma.space.createMany({ data });
}

async function main() {
  const [z1, z2] = await Promise.all([
    prisma.zone.create({ data: { code: 'Z1', name: 'Centro' } }),
    prisma.zone.create({ data: { code: 'Z2', name: 'Periférico' } }),
  ]);

  await createSpaces(z1.id, 1, 120, 'COMMON');
  await createSpaces(z1.id, 121, 135, 'MOTO');
  await createSpaces(z1.id, 136, 140, 'DISABLED');

  await createSpaces(z2.id, 1, 200, 'COMMON');
  await createSpaces(z2.id, 201, 220, 'MOTO');
  await createSpaces(z2.id, 221, 230, 'DISABLED');

  await prisma.rate.createMany({
    data: [
      { zoneId: z1.id, type: 'COMMON', pricePerMinute: 0.8, minPurchaseMinutes: 15, maxContinuousMinutes: 240, graceMinutes: 5 },
      { zoneId: z1.id, type: 'MOTO', pricePerMinute: 0.5, minPurchaseMinutes: 15, maxContinuousMinutes: 240, graceMinutes: 5 },
      { zoneId: z1.id, type: 'DISABLED', pricePerMinute: 0, minPurchaseMinutes: 0, maxContinuousMinutes: 120, graceMinutes: 10 },
      { zoneId: z2.id, type: 'COMMON', pricePerMinute: 0.8, minPurchaseMinutes: 15, maxContinuousMinutes: 240, graceMinutes: 5 },
      { zoneId: z2.id, type: 'MOTO', pricePerMinute: 0.5, minPurchaseMinutes: 15, maxContinuousMinutes: 240, graceMinutes: 5 },
      { zoneId: z2.id, type: 'DISABLED', pricePerMinute: 0, minPurchaseMinutes: 0, maxContinuousMinutes: 120, graceMinutes: 10 },
    ],
  });
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
