$ErrorActionPreference = 'Stop'
$random = [System.Random]::new(53245)
$cities = @(
    @{ Name='Mumbai'; Factor=1.65; Localities=@('Harbor View','Palm Grove','Cedar Park','Lakefront','Green Avenue','Sunrise Enclave') },
    @{ Name='Delhi'; Factor=1.18; Localities=@('Rosewood','Metro Heights','Shanti Vihar','Civic Greens','Riverbend','Pearl Residency') },
    @{ Name='Bengaluru'; Factor=1.25; Localities=@('Tech Park West','Orchid Lane','Mango Grove','Skyline Layout','Maple Cross','Garden Square') },
    @{ Name='Hyderabad'; Factor=0.93; Localities=@('Charminar Gardens','Pearl City','Cloud Nine','Olive District','Meadow Walk','Bluebell Enclave') },
    @{ Name='Pune'; Factor=0.92; Localities=@('University Circle','Silver Springs','Hillview','Aster Park','Central Grove','Crescent Bay') },
    @{ Name='Chennai'; Factor=0.90; Localities=@('Marina Vista','Coral Gardens','Temple Town','Rain Tree Park','Coastal Enclave','Jasmine Square') },
    @{ Name='Kolkata'; Factor=0.72; Localities=@('Victoria Greens','Lake Gardens','Banyan Court','Eastbank','Orchid Residency','Crescent Park') },
    @{ Name='Ahmedabad'; Factor=0.70; Localities=@('Sabarmati View','Lotus Enclave','Heritage Square','Riverstone','Amber Park','Clover Court') },
    @{ Name='Jaipur'; Factor=0.65; Localities=@('Pink City Heights','Aravali View','Moti Enclave','Royal Gardens','Amber Residency','Desert Bloom') },
    @{ Name='Lucknow'; Factor=0.60; Localities=@('Gomti Greens','Nawabi Enclave','Hazratganj Heights','Rose Garden','Crown Residency','Cedar Court') },
    @{ Name='Indore'; Factor=0.57; Localities=@('Palasia Park','Central Avenue','Lotus Lake','Vijay Nagar Greens','Maple Residency','Silver Oak') },
    @{ Name='Bhopal'; Factor=0.52; Localities=@('Lakeview Enclave','Van Vihar Greens','Saffron Square','Upper Lake Park','Cedar Residency','Sunset Court') }
)
$furnishing = @(@('Unfurnished',1.0),@('Semi-Furnished',1.13),@('Furnished',1.28))
$rows = [System.Collections.Generic.List[object]]::new()
foreach ($city in $cities) {
    for ($localityIndex=0; $localityIndex -lt 6; $localityIndex++) {
        $localityFactor = 0.84 + $localityIndex * 0.065
        for ($i=0; $i -lt 72; $i++) {
            $beds = $random.Next(1,6)
            $area = [Math]::Max(350, 350 + ($beds * 390) + ($random.Next(-13,14) * 20))
            $bathrooms = [Math]::Max(1,[Math]::Min(5,$beds + $random.Next(-1,2)))
            $balconies = [Math]::Max(0,[Math]::Min(4,[int][Math]::Round($beds * 0.55 + $random.Next(-1,2))))
            $f = $furnishing[$random.Next(0,3)]
            $rate = [Math]::Round(18.5 * $city.Factor * $localityFactor * $f[1] * (0.78 + $random.NextDouble() * 0.46),1)
            $sizeFactor = 0.83 + 0.17 * ($area / (430 + $beds * 390))
            $rent = [Math]::Max(4500,[int][Math]::Floor($area * $rate * $sizeFactor / 100) * 100)
            $houseType = if ($beds -le 4) { "$beds BHK Apartment" } else { 'Independent House' }
            $rows.Add([pscustomobject]@{ house_type=$houseType; locality=$city.Localities[$localityIndex]; city=$city.Name; area=$area; beds=$beds; bathrooms=$bathrooms; balconies=$balconies; furnishing=$f[0]; area_rate=$rate; rent=$rent })
        }
    }
}
$out = Join-Path (Split-Path $PSScriptRoot -Parent) 'data\rent_listings.csv'
$rows | Export-Csv -Path $out -NoTypeInformation -Encoding utf8
Write-Output "Wrote $($rows.Count) simulated rows to $out"
