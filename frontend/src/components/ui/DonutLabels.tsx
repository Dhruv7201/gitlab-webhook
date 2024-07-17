"use client";

import * as React from "react";
import { TrendingUp } from "lucide-react";
import { Label, Pie, PieChart } from "recharts";
import "./DonutLabels.css";

import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

type CharData = {
  label: string;
  count: number;
  fill: string;
};

const chartConfig = {
  total: {
    label: "Total",
  },
  Doing: {
    label: "Doing",
    color: "hsl(var(--chart-0))",
  },
  Doc: {
    label: "Doc",
    color: "hsl(var(--chart-2))",
  },
  testing: {
    label: "Testing",
    color: "hsl(var(--chart-3))",
  },
} as ChartConfig;

export function DonutLabels(selected:boolean, project_id:str) {
  const [chartData, setChartData] = React.useState<CharData[]>([]);
  const api = import.meta.env.VITE_API_URL;
  const getColor = (data: CharData[]) => {
    const colors = ["#FF6633", "#2563eb", "#FF33FF", "#FFFF99", "#00B3E6"];
    return data.map((entry, index) => ({
      ...entry,
      fill: colors[index % colors.length],
    }));
  };

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(api + "/donut_labels");
        const data = await response.json();
        setChartData(getColor(data));
      } catch (error) {
        console.error("Problem fetching chart data", error);
      }
    };
    fetchData();
  }, []);

  return (

    <> 
    {selected?<Card className="flex flex-col">
      <CardHeader className="items-center pb-0">
        <CardTitle>Pie Chart - Donut with Text</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 pb-0">
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square max-h-[250px]"
        >
          <PieChart>
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Pie
              data={chartData}
              dataKey="count"
              nameKey="label"
              innerRadius={60}
              strokeWidth={5}
            >
              <Label
                content={({ viewBox }) => {
                  if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                    return (
                      <text
                        x={viewBox.cx}
                        y={viewBox.cy}
                        textAnchor="middle"
                        dominantBaseline="middle"
                      >
                        <tspan
                          x={viewBox.cx}
                          y={viewBox.cy}
                          className="fill-foreground text-3xl font-bold"
                        >
                          {chartData.reduce(
                            (acc: number, { count }: { count: number }) =>
                              acc + count,
                            0
                          )}
                        </tspan>
                        <tspan
                          x={viewBox.cx}
                          y={(viewBox.cy || 0) + 24}
                          className="fill-muted-foreground"
                        >
                          Total
                        </tspan>
                      </text>
                    );
                  }
                }}
              />
            </Pie>
          </PieChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col gap-2 text-sm">
        <div className="flex items-center gap-2 font-medium leading-none">
          <TrendingUp size={16} />
          <span>Label Data</span>
        </div>
        <div className="leading-none text-muted-foreground">
          Showing total label count
        </div>
      </CardFooter>
    </Card>:<div></div>}
    </>
  );
}
