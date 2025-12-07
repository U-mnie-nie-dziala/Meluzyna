import { useState, useEffect, useRef } from 'react';
import { Building2, ChevronDown, Check } from 'lucide-react';
import { Sector } from '../types';

interface SectorSelectorProps {
  selectedSector: Sector | '';
  onSectorChange: (sector: Sector | '') => void;
}



export default function SectorSelector({ selectedSector, onSectorChange }: SectorSelectorProps) {
  const [sectors, setSectors] = useState<Array<{ value: Sector; label: string }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/categories')
      .then(res => res.json())
      .then(data => {
        const formattedSectors = data.map((item: { pkd: string; nazwa: string }) => ({
          value: item.pkd,
          label: item.nazwa
        }));
        setSectors(formattedSectors);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch sectors:', err);
        setLoading(false);
      });
  }, []);

  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectedLabel = sectors.find(s => s.value === selectedSector)?.label || 'Wybierz sektor...';

  return (
    <div className="relative rounded-lg" ref={dropdownRef}>
      <label htmlFor="sector" className="block rounded-lg text-sm font-semibold text-slate-700 mb-2">
        Wybierz Sektor
      </label>

      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full pl-11 pr-4 py-3 bg-white border rounded-lg text-left flex items-center justify-between
                   transition-all duration-200 outline-none
                   ${isOpen
            ? 'border-blue-500 ring-2 ring-blue-500/20'
            : 'border-slate-300 hover:border-slate-400'}`}
      >
        <span className={`font-medium ${selectedSector ? 'text-slate-900' : 'text-slate-500'}`}>
          {selectedLabel}
        </span>
        <ChevronDown
          className={`w-5 h-5 text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      <div className="absolute left-3 top-11 pointer-events-none">
        <Building2 className="w-5 h-5 text-slate-400" />
      </div>

      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white border border-slate-200 rounded-lg shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-100">
          <div className="max-h-[300px] overflow-y-auto py-1">
            {loading ? (
              <div className="px-4 py-3 text-slate-500 italic">Ładowanie...</div>
            ) : (
              sectors.map((sector) => (
                <button
                  key={sector.value}
                  onClick={() => {
                    onSectorChange(sector.value);
                    setIsOpen(false);
                  }}
                  className="w-full px-4 py-2.5 text-left flex items-center justify-between hover:bg-slate-50 transition-colors group"
                >
                  <span className={`font-medium ${selectedSector === sector.value ? 'text-blue-600' : 'text-slate-700'}`}>
                    {sector.label}
                  </span>
                  {selectedSector === sector.value && (
                    <Check className="w-4 h-4 text-blue-600" />
                  )}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );

}
