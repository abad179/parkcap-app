import express, { Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';

const app = express();
app.use(express.json());
app.use(cors());
app.use(helmet());

app.get('/health', (_req: Request, res: Response) => res.json({ status: 'ok' }));

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server listening on ${port}`);
});
