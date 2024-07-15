import { DonutLabels } from "@/components/ui/DonutLabels";
import { AreaChartCom } from "@/components/ui/AreaChart";
import { Barchart } from "@/components/ui/BarChart";

const ChartsPage = () => {
  return (
    <>
    <div className="container mx-auto p-4 flex flex-row gap-4 h-full w-full">
      <div className="flex flex-col gap-4 w-1/2 h-full">
        <DonutLabels />
      </div>
      <div className="flex flex-col gap-4 w-1/2 h-full">
        <AreaChartCom />
      </div>
      </div>
      <div className="row">
      <div className="flex flex-col gap-4 w-1/2 h-full">
        <Barchart />
      </div>
      </div>
      </>
  );
};

export default ChartsPage;
