import { Building2 } from 'lucide-react';
import { Sector } from '../types';

interface SectorSelectorProps {
  selectedSector: Sector | '';
  onSectorChange: (sector: Sector | '') => void;
}

const sectors: Array<{ value: Sector; label: string }> = [
  { value: 'technology', label: 'Technologia' },
  { value: 'healthcare', label: 'Służba Zdrowia' },
  { value: 'finance', label: 'Financial Services' },
  { value: 'energy', label: 'Energy & Resources' },
  { value: 'consumer', label: 'Consumer Goods' },
  { value: 'industrial', label: 'Industrial' },
  { value: 'realestate', label: 'Real Estate' },
  { value: 'utilities', label: 'Utilities' },
];

export default function SectorSelector({ selectedSector, onSectorChange }: SectorSelectorProps) {
  return (
    <div>
      <label htmlFor="sector" className="block text-sm font-semibold text-slate-700 mb-2">
        Wybierz Sektor
      </label>
      <div className="relative">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <Building2 className="w-5 h-5 text-slate-400" />
        </div>
        <select
          id="sector"
          value={selectedSector}
          onChange={(e) => onSectorChange(e.target.value as Sector | '')}
          className="w-full pl-11 pr-4 py-3 bg-white border border-slate-300 rounded-lg
                   text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500
                   focus:border-transparent transition-all cursor-pointer hover:border-slate-400"
        >
          <option value="">Wybierz sektor...</option>
          {sectors.map((sector) => (
            <option key={sector.value} value={sector.value}>
              {sector.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
