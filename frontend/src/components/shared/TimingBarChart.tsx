import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function TimingBarChart({ perRoundNs }: { perRoundNs: number[] }) {
  const data = perRoundNs.map((ns, index) => ({
    round: `R${index + 1}`,
    ns,
  }));

  return (
    <div className="h-52">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="var(--cl-border-light)" strokeDasharray="4 4" vertical={false} />
          <XAxis
            dataKey="round"
            tick={{ fontSize: 11, fill: "var(--cl-text-secondary)" }}
            tickLine={false}
            axisLine={{ stroke: "var(--cl-border)" }}
          />
          <YAxis
            width={56}
            tick={{ fontSize: 11, fill: "var(--cl-text-secondary)" }}
            tickLine={false}
            axisLine={{ stroke: "var(--cl-border)" }}
          />
          <Tooltip
            formatter={(value: any) => [`${Number(value).toFixed(0)} ns`, "Round time"]}
            labelFormatter={(label) => `${label}`}
          />
          <Bar dataKey="ns" fill="var(--cl-primary)" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
