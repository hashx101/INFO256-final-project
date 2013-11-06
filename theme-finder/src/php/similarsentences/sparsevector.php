<?php

class SparseVector{
	
	public $features = array();
	
	public function __construct($featureArray=array()){
		$this->features = $featureArray;
		return $this;
	}
	
	public function getFeatureValue($featureID){
		if(array_key_exists($featureID, $this->features)){
			return $this->features[$featureID];
		}else{
			return 0;
		}
	}
	
	public function setFeatureValue($featureID, $value){
		$this->features[$featureID] = $value;
		return $this;
	}
	
	public function features(){
		return $this->features;
	}
	
	public function vectorAdd($sparseVector){
		$vector2 = $sparseVector->features();
		$vector1 = $this->features();
		$result = array();
		foreach(array_keys($vector1) as $featureID){
			$result[$featureID] = $vector1[$featureID];
		}
		foreach(array_keys($vector2) as $featureID){
			if(array_key_exists($featureID, $result)){
				$result[$featureID] += $vector2[$featureID];
			}else{
				$result[$featureID] = $vector2[$featureID];
			}
		}
		$answer = new SparseVector($result);
		return $answer;
	}
	
	public function dotProduct($sparseVector){
		$vector2 = $sparseVector->features();
		$f = $this->features;
		$dotProduct = 0;
		if(count($this->features) > 0){
		foreach(array_keys($vector2) as $featureID){
			if(array_key_exists($featureID, $f)){
				$dotProduct += ($f[$featureID] * $vector2[$featureID]);
			}
		}
		}
		return $dotProduct;
	}
	
	public function scalarMultiply($scalar){
		$result = array();
		$f = $this->features;
		if(count($this->features) > 0){
		foreach(array_keys($f) as $featureID){
			$result[$featureID] = $f[$featureID]*$scalar;
		}
		}
		return new SparseVector($result);
	}
	
	public function normalize(){
		$sum = 0;
		if(count($this->features) > 0){
			foreach(array_keys($this->features) as $featureID){
				$sum += abs($this->features[$featureID]);
			}
			if($sum > 0){
			foreach(array_keys($this->features) as $featureID){
				$this->features[$featureID] = $this->features[$featureID]/$sum;
			}
			}	
		}
	}
	
}

?>