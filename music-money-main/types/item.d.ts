export interface Item {
  id: string;
  name: string;
  description: string;
  category: string;
  status: 'active' | 'inactive' | 'pending';
  price: number;
  inventory: number;
  createdAt: string;
  updatedAt: string;
  specifications: {
    weight: string;
    dimensions: string;
    color: string;
    material: string;
  };
}