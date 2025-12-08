#!/usr/bin/env python3
"""
MeshCore Signal Calculator - Signal propagation and coverage analysis

Calculates signal strength, coverage areas, and interference patterns for
MeshCore mesh networks. Provides realistic signal propagation modeling for
visualization and network planning.

Features:
- Free-space path loss calculation
- Obstacle attenuation modeling
- Multi-path interference estimation
- Coverage area computation
- Signal-to-noise ratio (SNR) analysis
- Mesh network optimization suggestions

Version: v1.2.14
Author: Fred Porter
Date: December 7, 2025
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """Environment types affecting signal propagation."""
    OPEN = "open"           # Open field, minimal obstacles
    URBAN = "urban"         # Urban environment, buildings
    INDOOR = "indoor"       # Indoor environment
    FOREST = "forest"       # Forested area
    INDUSTRIAL = "industrial"  # Industrial zone


@dataclass
class SignalParameters:
    """Signal transmission parameters."""
    frequency_mhz: float = 915.0    # ISM band frequency (MHz)
    tx_power_dbm: float = 20.0      # Transmit power (dBm)
    tx_gain_dbi: float = 2.0        # Transmit antenna gain (dBi)
    rx_gain_dbi: float = 2.0        # Receive antenna gain (dBi)
    noise_floor_dbm: float = -110.0 # Noise floor (dBm)
    sensitivity_dbm: float = -95.0  # Receiver sensitivity (dBm)


@dataclass
class SignalResult:
    """Signal calculation result."""
    distance_m: float          # Distance in meters
    path_loss_db: float        # Path loss in dB
    rx_power_dbm: float        # Received power in dBm
    signal_strength_pct: int   # Signal strength (0-100%)
    snr_db: float              # Signal-to-noise ratio
    link_quality: str          # excellent/good/fair/poor/none


class SignalCalculator:
    """
    Calculate signal strength and propagation for mesh networks.
    
    Uses simplified RF propagation models suitable for mesh network
    planning and visualization.
    """
    
    # Environment-specific path loss exponents
    PATH_LOSS_EXPONENTS = {
        Environment.OPEN: 2.0,        # Free space
        Environment.URBAN: 3.5,       # Urban obstacles
        Environment.INDOOR: 2.5,      # Indoor walls
        Environment.FOREST: 3.0,      # Foliage attenuation
        Environment.INDUSTRIAL: 4.0   # Heavy metal structures
    }
    
    # Additional attenuation per meter (dB/m)
    ATTENUATION_FACTORS = {
        Environment.OPEN: 0.0,
        Environment.URBAN: 0.05,
        Environment.INDOOR: 0.1,
        Environment.FOREST: 0.08,
        Environment.INDUSTRIAL: 0.15
    }
    
    def __init__(self, params: Optional[SignalParameters] = None):
        """
        Initialize signal calculator.
        
        Args:
            params: Signal transmission parameters
        """
        self.params = params or SignalParameters()
    
    def calculate_free_space_path_loss(self, distance_m: float) -> float:
        """
        Calculate free-space path loss (FSPL).
        
        FSPL (dB) = 20*log10(d) + 20*log10(f) + 20*log10(4π/c)
        
        Args:
            distance_m: Distance in meters
            
        Returns:
            Path loss in dB
        """
        if distance_m <= 0:
            return 0.0
        
        # Wavelength in meters
        c = 299792458  # Speed of light (m/s)
        wavelength = c / (self.params.frequency_mhz * 1e6)
        
        # FSPL formula
        fspl = 20 * math.log10(distance_m) + \
               20 * math.log10(self.params.frequency_mhz) + \
               20 * math.log10(4 * math.pi / c) + \
               120  # Constant factor
        
        return fspl
    
    def calculate_path_loss(
        self,
        distance_m: float,
        environment: Environment = Environment.URBAN
    ) -> float:
        """
        Calculate path loss with environment-specific model.
        
        Uses log-distance path loss model:
        PL(d) = PL(d0) + 10*n*log10(d/d0) + Xσ
        
        Args:
            distance_m: Distance in meters
            environment: Environment type
            
        Returns:
            Path loss in dB
        """
        if distance_m <= 0:
            return 0.0
        
        # Reference distance (1 meter)
        d0 = 1.0
        
        # Get path loss exponent for environment
        n = self.PATH_LOSS_EXPONENTS.get(environment, 2.0)
        
        # Calculate base path loss
        pl_d0 = self.calculate_free_space_path_loss(d0)
        path_loss = pl_d0 + 10 * n * math.log10(distance_m / d0)
        
        # Add environment-specific attenuation
        attenuation_factor = self.ATTENUATION_FACTORS.get(environment, 0.0)
        path_loss += attenuation_factor * distance_m
        
        return path_loss
    
    def calculate_received_power(
        self,
        distance_m: float,
        environment: Environment = Environment.URBAN
    ) -> float:
        """
        Calculate received power at distance.
        
        Rx Power = Tx Power + Tx Gain + Rx Gain - Path Loss
        
        Args:
            distance_m: Distance in meters
            environment: Environment type
            
        Returns:
            Received power in dBm
        """
        path_loss = self.calculate_path_loss(distance_m, environment)
        
        rx_power = (self.params.tx_power_dbm +
                   self.params.tx_gain_dbi +
                   self.params.rx_gain_dbi -
                   path_loss)
        
        return rx_power
    
    def calculate_snr(self, rx_power_dbm: float) -> float:
        """
        Calculate signal-to-noise ratio.
        
        SNR = Rx Power - Noise Floor
        
        Args:
            rx_power_dbm: Received power in dBm
            
        Returns:
            SNR in dB
        """
        return rx_power_dbm - self.params.noise_floor_dbm
    
    def rx_power_to_percentage(self, rx_power_dbm: float) -> int:
        """
        Convert received power to percentage (0-100).
        
        Maps sensitivity to 0% and tx_power to 100%.
        
        Args:
            rx_power_dbm: Received power in dBm
            
        Returns:
            Signal strength percentage
        """
        min_power = self.params.sensitivity_dbm
        max_power = self.params.tx_power_dbm
        
        if rx_power_dbm <= min_power:
            return 0
        elif rx_power_dbm >= max_power:
            return 100
        else:
            # Linear mapping
            pct = ((rx_power_dbm - min_power) / (max_power - min_power)) * 100
            return max(0, min(100, int(pct)))
    
    def assess_link_quality(self, snr_db: float) -> str:
        """
        Assess link quality based on SNR.
        
        Args:
            snr_db: Signal-to-noise ratio in dB
            
        Returns:
            Quality assessment string
        """
        if snr_db >= 25:
            return "excellent"
        elif snr_db >= 15:
            return "good"
        elif snr_db >= 10:
            return "fair"
        elif snr_db >= 5:
            return "poor"
        else:
            return "none"
    
    def calculate_signal(
        self,
        distance_m: float,
        environment: Environment = Environment.URBAN
    ) -> SignalResult:
        """
        Complete signal analysis for given distance.
        
        Args:
            distance_m: Distance in meters
            environment: Environment type
            
        Returns:
            SignalResult with all metrics
        """
        path_loss = self.calculate_path_loss(distance_m, environment)
        rx_power = self.calculate_received_power(distance_m, environment)
        snr = self.calculate_snr(rx_power)
        signal_pct = self.rx_power_to_percentage(rx_power)
        quality = self.assess_link_quality(snr)
        
        return SignalResult(
            distance_m=distance_m,
            path_loss_db=path_loss,
            rx_power_dbm=rx_power,
            signal_strength_pct=signal_pct,
            snr_db=snr,
            link_quality=quality
        )
    
    def calculate_max_range(
        self,
        environment: Environment = Environment.URBAN,
        min_snr_db: float = 5.0
    ) -> float:
        """
        Calculate maximum communication range.
        
        Binary search to find distance where SNR drops below threshold.
        
        Args:
            environment: Environment type
            min_snr_db: Minimum acceptable SNR
            
        Returns:
            Maximum range in meters
        """
        # Binary search bounds
        low = 0.0
        high = 10000.0  # 10km max search
        tolerance = 1.0  # 1 meter tolerance
        
        while high - low > tolerance:
            mid = (low + high) / 2
            result = self.calculate_signal(mid, environment)
            
            if result.snr_db >= min_snr_db:
                low = mid  # Can go further
            else:
                high = mid  # Too far
        
        return low
    
    def calculate_coverage_area(
        self,
        environment: Environment = Environment.URBAN,
        grid_resolution: int = 20
    ) -> List[List[int]]:
        """
        Calculate signal coverage heatmap.
        
        Generates grid showing signal strength at each point.
        
        Args:
            environment: Environment type
            grid_resolution: Grid size (NxN)
            
        Returns:
            2D array of signal percentages
        """
        max_range = self.calculate_max_range(environment)
        cell_size = max_range / grid_resolution
        
        coverage = []
        
        for row in range(grid_resolution):
            coverage_row = []
            for col in range(grid_resolution):
                # Calculate distance from center
                dx = (col - grid_resolution / 2) * cell_size
                dy = (row - grid_resolution / 2) * cell_size
                distance = math.sqrt(dx**2 + dy**2)
                
                result = self.calculate_signal(distance, environment)
                coverage_row.append(result.signal_strength_pct)
            
            coverage.append(coverage_row)
        
        return coverage
    
    def optimize_repeater_placement(
        self,
        source_distance_m: float,
        target_distance_m: float,
        environment: Environment = Environment.URBAN
    ) -> Dict:
        """
        Calculate optimal repeater placement.
        
        Args:
            source_distance_m: Distance from source to target
            target_distance_m: Desired final range
            environment: Environment type
            
        Returns:
            Optimization recommendations
        """
        max_range = self.calculate_max_range(environment)
        
        # Calculate number of hops needed
        hops_needed = math.ceil(target_distance_m / max_range)
        
        # Optimal spacing
        spacing = target_distance_m / hops_needed
        
        return {
            'max_single_hop': max_range,
            'total_distance': target_distance_m,
            'hops_required': hops_needed,
            'repeaters_needed': max(0, hops_needed - 1),
            'optimal_spacing': spacing,
            'positions': [spacing * i for i in range(1, hops_needed)]
        }


def demo_signal_calculator():
    """Demonstrate signal calculator functionality."""
    
    print("=" * 80)
    print("MeshCore Signal Calculator Demo - v1.2.14")
    print("=" * 80)
    print()
    
    calc = SignalCalculator()
    
    # Demo 1: Signal at various distances
    print("Demo 1: Signal Strength vs Distance (Urban)")
    print("-" * 80)
    
    distances = [10, 50, 100, 250, 500, 1000]
    
    for distance in distances:
        result = calc.calculate_signal(distance, Environment.URBAN)
        print(f"  {distance:>4}m: "
              f"{result.signal_strength_pct:>3}% | "
              f"SNR: {result.snr_db:>5.1f} dB | "
              f"Quality: {result.link_quality}")
    print()
    
    # Demo 2: Environment comparison
    print("Demo 2: Environment Impact (100m)")
    print("-" * 80)
    
    for env in Environment:
        result = calc.calculate_signal(100, env)
        print(f"  {env.value:12}: "
              f"{result.signal_strength_pct:>3}% | "
              f"SNR: {result.snr_db:>5.1f} dB | "
              f"Rx: {result.rx_power_dbm:>6.1f} dBm")
    print()
    
    # Demo 3: Maximum range
    print("Demo 3: Maximum Communication Range")
    print("-" * 80)
    
    for env in Environment:
        max_range = calc.calculate_max_range(env)
        print(f"  {env.value:12}: {max_range:>6.1f} meters")
    print()
    
    # Demo 4: Repeater optimization
    print("Demo 4: Repeater Placement Optimization")
    print("-" * 80)
    
    target_distance = 1500  # 1.5km
    optimization = calc.optimize_repeater_placement(
        0, target_distance, Environment.URBAN
    )
    
    print(f"  Target Distance: {target_distance}m")
    print(f"  Max Single Hop:  {optimization['max_single_hop']:.1f}m")
    print(f"  Hops Required:   {optimization['hops_required']}")
    print(f"  Repeaters Needed: {optimization['repeaters_needed']}")
    print(f"  Optimal Spacing:  {optimization['optimal_spacing']:.1f}m")
    
    if optimization['positions']:
        print(f"  Positions: ", end="")
        print(", ".join(f"{pos:.1f}m" for pos in optimization['positions']))
    print()
    
    # Demo 5: Coverage heatmap (small grid)
    print("Demo 5: Coverage Heatmap (8x8 grid, Urban)")
    print("-" * 80)
    
    coverage = calc.calculate_coverage_area(Environment.URBAN, grid_resolution=8)
    
    from core.ui.grid_renderer import Symbols
    
    for row in coverage:
        heatmap_row = "  "
        for signal in row:
            heatmap_row += Symbols.signal_gradient(signal) + " "
        print(heatmap_row)
    
    print()
    print("  Legend: █=100% ▓=75% ▒=50% ░=25% ' '=0%")
    print()
    
    print("✅ Signal calculator demo complete!")


if __name__ == "__main__":
    demo_signal_calculator()
